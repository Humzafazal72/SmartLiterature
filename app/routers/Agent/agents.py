import requests
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from .schema import AgentState, Clarification, KeywordExtractionOutput, Selection

clarifier_llm = ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(Clarification)
keyword_llm = ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(KeywordExtractionOutput)
Selecter_llm = ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(Selection)

def OpenAlex_searcher(state: AgentState):
    """
    Given a list of keywords, return 10 most relevant papers for each keyword 
    from OpenAlex, ordered by citation count.
    Returns a dict where key is paper title and value is [authors, doi, venue, date]
    """
    results_dict = {}
    
    for query in state['keywords']['openalex_keywords']:
        # OpenAlex API endpoint
        url = 'https://api.openalex.org/works'
        
        # Parameters: search query, 10 results per page, sorted by citations
        params = {
            'search': query,
            'per-page': 10,
            'sort': 'cited_by_count:desc'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            for work in data.get('results', []):
                # Extract title
                title = work.get('title', 'No title available')
                if not title or title in results_dict:
                    continue  # Skip duplicates or empty titles
                
                # Extract authors
                authors = []
                for authorship in work.get('authorships', []):
                    author_name = authorship.get('author', {}).get('display_name', '')
                    if author_name:
                        authors.append(author_name)
                
                # Extract DOI
                doi = work.get('doi', '')
                if doi and doi.startswith('https://doi.org/'):
                    doi = doi.replace('https://doi.org/', '')
                
                # Extract journal/conference (venue)
                venue = 'Unknown'
                primary_location = work.get('primary_location', {})
                if primary_location:
                    source = primary_location.get('source', {})
                    if source:
                        venue = source.get('display_name', 'Unknown')
                
                # Extract publication date
                publication_date = work.get('publication_date', '')
                if not publication_date:
                    publication_date = str(work.get('publication_year', ''))
                
                # Add to results dictionary
                results_dict[title] = [authors, doi, venue, publication_date]
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for query '{query}': {e}")
            continue
        except ValueError as e:
            print(f"Error parsing JSON response for query '{query}': {e}")
            continue
    
    return {"initial_metadata": results_dict}


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
    - OpenAlex (https://openalex.org)

    You will receive a short research topic description from the user.

    Your task is to analyze the description and return a set of structured keywords and search phrases optimized for OpenAlex.

    You MUST return your output as an instance of the following schema:

    Guidelines:
    - Avoid generic terms like "paper", "study", "research"
    - Prefer specific methods (e.g., CNN, BERT, PCA), tasks (e.g., segmentation, prediction), and datasets (e.g., CHB-MIT, ImageNet)
    - If user input is vague, extract the most relevant, inferable terms — don't leave the list empty
    - All outputs should be lowercase unless referring to acronyms (e.g., EEG, GNN, LSTM)
    """
    )
    
    keyworder_response = keyword_llm.invoke([system_prompt] + state['messages'])

    return {"keywords":keyworder_response}


def Selector_1(state: AgentState):
    title_list = list(state['initial_metadata'].keys())
    titles = title_list[ : len(title_list) // 2]

    prompt = SystemMessage(content=f"""
    You are an expert research assistant helping to select the most relevant papers for a literature review.

    Below is a chat between the user and the Clarifier AI. This chat captures the research needs and requirements:
    {state['messages']}

    Candidate paper titles:
    {titles}

    Task:
    - Select ONLY the papers that are directly aligned with the users research needs and can be used in literature review.
    - Use strict topical alignment as the main criterion.
    - Prioritize papers that explicitly match the research requirements.
    - Avoid redundancy: if multiple surveys or reviews overlap heavily, keep only the strongest one or two.
    - Include both (a) core domain papers and (b) a small number of foundational or methodological works if they are clearly relevant.
    - Exclude irrelevant, overly broad, or generic titles.
    - Do NOT summarize the chat or papers, only output the selected titles.

    Output format:
    - Return the selected titles as a Python list of strings.
    """)

    result = Selecter_llm.invoke([prompt]) 
    return {"selected_papers_1": result["paper_titles"]}


def Selector_2(state: AgentState):
    title_list = list(state['initial_metadata'].keys())
    titles = title_list[len(title_list) // 2 :]

    prompt = SystemMessage(content=f"""
    You are an expert research assistant helping to select the most relevant papers for a literature review.

    Below is a chat between the user and the Clarifier AI. This chat captures the research needs and requirements:
    {state['messages']}

    Candidate paper titles:
    {titles}

    Task:
    - Select ONLY the papers that are directly aligned with the users research needs and can be used in literature review.
    - Use strict topical alignment as the main criterion.
    - Prioritize papers that explicitly match the research requirements.
    - Avoid redundancy: if multiple surveys or reviews overlap heavily, keep only the strongest one or two.
    - Include both (a) core domain papers and (b) a small number of foundational or methodological works if they are clearly relevant.
    - Exclude irrelevant, overly broad, or generic titles.
    - Do NOT summarize the chat or papers, only output the selected titles.

    Output format:
    - Return the selected titles as a Python list of strings.
    """)

    result = Selecter_llm.invoke([prompt])
    return {"selected_papers_2": result["paper_titles"]}


def merge_results(state: AgentState):    
    selected_papers = state.get("selected_papers_1", []) + state.get("selected_papers_2", [])
    final_metadata = {k: state['initial_metadata'][k] for k in selected_papers if k in state['initial_metadata']}
    return {"final_metadata":final_metadata}


def clarifier_router(state: AgentState):
    if state['clarification']['needs_improvement']:
        return "end"
    else:
        return "continue"