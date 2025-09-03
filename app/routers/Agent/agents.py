import requests
from scholarly import scholarly
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage,SystemMessage,HumanMessage
from schema import AgentState, Clarification, KeywordExtractionOutput, Selection


clarifier_llm = ChatGroq(model="moonshotai/kimi-k2-instruct").with_structured_output(Clarification)
keyword_llm = ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(KeywordExtractionOutput)
Selecter_llm = ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(Selection)


def scholar_searcher(state: AgentState):
    """
    Given a list of keywords. it return 10 most revlevent papers for each keyword.
    """
    title_results = set()

    for query in state['keywords']['google_scholar_queries']:
        count = 0
        for pub in scholarly.search_pubs(query):
            title_results.add(pub["bib"]["title"])
            count += 1
            if count >= 10:
                break 
    
    return {"scholar_titles": title_results}


def clarifier(state:AgentState):
    system_prompt = SystemMessage(content="""
        You are a research assistant. The user will provide you with a research paper topic or description.
        
        Your job is to check if the description includes:
        1. Research domain
        2. Problem being solved
        3. Method or technique used
        4. Any dataset mentioned
        
        If ANY of these elements are missing or unclear, set needs_improvement to True and provide specific questions in the 'questions' field to gather the missing information.
        
        If all elements are present and clear, set needs_improvement to False and questions can be null or empty.
        
        Example response format:
        - If missing info: {"needs_improvement": true, "questions": ["What specific problem are you trying to solve?", "Which dataset will you use?"]}
        - If complete: {"needs_improvement": false, "questions": null}
        """
    )
    clarifier_response = clarifier_llm.invoke([system_prompt]+[state["messages"][-1]])

    return {"clarification":clarifier_response}

def keyworder(state:AgentState):
    system_prompt = SystemMessage(content="""
    You are a research assistant trained to extract keywords for academic paper searches, specifically for:
    - Google Scholar (https://scholar.google.com)

    You will receive a short research topic description from the user.

    Your task is to analyze the description and return a set of structured keywords and search phrases optimized for Google Scholar.

    You MUST return your output as an instance of the following schema:

    Guidelines:
    - Avoid generic terms like "paper", "study", "research"
    - Prefer specific methods (e.g., CNN, BERT, PCA), tasks (e.g., segmentation, prediction), and datasets (e.g., CHB-MIT, ImageNet)
    - If user input is vague, extract the most relevant, inferable terms — don't leave the list empty
    - All outputs should be lowercase unless referring to acronyms (e.g., EEG, GNN, LSTM)

    Only return a valid Python object matching the schema exactly.
    Do not include any extra fields, strings, comments, or explanations.
    Avoid quoting the entire object as a string.
    """
    )
    
    keyworder_response = keyword_llm.invoke([system_prompt] + state['messages'])

    return {"keywords":keyworder_response}
    

def Selector_1(state: AgentState):
    description = state['messages'][-1].content
    title_list = list(state['scholar_titles'])
    titles = title_list[ : len(title_list) // 2]

    prompt = SystemMessage(content=f"""
    You are an expert research assistant helping to select the most relevant papers for a literature review.

    Paper description:
    {description}

    Candidate paper titles:
    {titles}

    Task:
    - Select ONLY the papers that are directly useful for the literature review.
    - Prioritize papers that explicitly match the research description.
    - Avoid redundancy: if multiple surveys or reviews overlap heavily, pick the strongest one or two.
    - Include both (a) core domain papers and (b) a small number of foundational or methodological works if they are clearly relevant.
    - Do NOT return irrelevant, overly broad, or generic titles.
    """)

    result = Selecter_llm.invoke([prompt]) 
    return {"selected_papers_1": result["paper_titles"]}


def Selector_2(state: AgentState):
    description = state['messages'][-1].content
    title_list = list(state['scholar_titles'])
    titles = title_list[len(title_list) // 2 :]

    prompt = SystemMessage(content=f"""
    You are an expert research assistant helping to select the most relevant papers for a literature review. 

    Paper description:
    {description}

    Candidate paper titles:
    {titles}

    Task:
    - Select ONLY the papers that are directly useful for the literature review.
    - Prioritize papers that explicitly match the research description.
    - Avoid redundancy: if multiple surveys or reviews overlap heavily, pick the strongest one or two.
    - Include both (a) core domain papers and (b) a small number of foundational or methodological works if they are clearly relevant.
    - Do NOT return irrelevant, overly broad, or generic titles.
    """)

    result = Selecter_llm.invoke([prompt])
    return {"selected_papers_2": result["paper_titles"]}

def metadata_getter(state: AgentState):
    """
    Query Crossref for each paper title. 
    If Crossref fails, fallback to Google Scholar (scholarly).
    """
    base_url = "https://api.crossref.org/works"
    headers = {"User-Agent": "PaperMetadataFetcher/1.0 (mailto:your-email@example.com)"}
    
    results = {}
    titles = state['selected_papers_1'] + state['selected_papers_2']
    
    for title in titles:
        params = {"query.title": title, "rows": 1}
        response = requests.get(base_url, params=params, headers=headers)
        
        doi, journal, authors_str, pub_date = "N/A", "N/A", "N/A", "N/A"
        
        if response.status_code == 200:
            items = response.json().get("message", {}).get("items", [])
            if items:
                item = items[0]
                doi = item.get("DOI", "N/A")
                journal = (
                    item.get("container-title", ["N/A"])[0]
                    if item.get("container-title")
                    else "N/A"
                )
                authors = []
                for a in item.get("author", []):
                    name_parts = []
                    if "given" in a:
                        name_parts.append(a["given"])
                    if "family" in a:
                        name_parts.append(a["family"])
                    authors.append(" ".join(name_parts))
                authors_str = ", ".join(authors) if authors else "N/A"
                
                # Publication date
                date_parts = (
                    item.get("published-print", {}).get("date-parts")
                    or item.get("published-online", {}).get("date-parts")
                )
                if date_parts:
                    pub_date = "-".join(map(str, date_parts[0]))  # YYYY or YYYY-MM-DD
        
        # Fallback to Google Scholar if Crossref failed
        if journal == "N/A" or authors_str == "N/A" or pub_date == "N/A":
            try:
                search_query = scholarly.search_pubs(title)
                paper = next(search_query, None)
                if paper:
                    bib = paper.get("bib", {})
                    journal = bib.get("venue", journal)  # venue is journal/conference in scholarly
                    authors_str = ", ".join(bib.get("author", [])) if bib.get("author") else authors_str
                    pub_date = str(bib.get("pub_year", pub_date))
            except Exception as e:
                print(f"Google Scholar fallback failed for '{title}': {e}")
        
        results[title] = [doi, journal, authors_str, pub_date]
    
    return {"metadata": results}


def clarifier_router(state: AgentState):
    if state['clarification']['needs_improvement']:
        return "end"
    else:
        return "continue"
    

