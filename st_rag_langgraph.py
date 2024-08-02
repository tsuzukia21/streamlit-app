import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph
from typing import List, Annotated, Literal, Sequence, TypedDict
from langgraph.graph import END, StateGraph, START
import asyncio
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
import streamlit_antd_components as sac

class RouteQuery(BaseModel):
    """ユーザーのクエリを最も関連性の高いデータソースにルーティングします。"""

    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="ユーザーの質問に応じて、ウェブ検索またはベクターストアにルーティングします。",
    )


class GradeDocuments(BaseModel):
    """取得された文書の関連性チェックのためのバイナリスコア。"""

    binary_score: str = Field(
        description="文書が質問に関連しているかどうか、「yes」または「no」"
    )


class GradeHallucinations(BaseModel):
    """生成された回答における幻覚の有無を示すバイナリスコア。"""

    binary_score: str = Field(
        description="回答が事実に基づいているかどうか、「yes」または「no」"
    )

class GradeAnswer(BaseModel):
    """回答が質問に対処しているかどうかを評価するバイナリスコア。"""

    binary_score: str = Field(
        description="回答が質問に対処しているかどうか、「yes」または「no」"
    )

class GraphState(TypedDict):
    """
    グラフの状態を表します。

    属性:
        question: 質問
        generation: LLM生成
        documents: 文書のリスト
    """

    question: str
    generation: str
    documents: List[str]

async def route_question(state):
    st.session_state.status.update(label=f"**---ROUTE QUESTION---**", state="running", expanded=True)
    st.session_state.log += "---ROUTE QUESTION---" + "\n\n"
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=st.session_state.openai_api_key)
    structured_llm_router = llm.with_structured_output(RouteQuery)

    system = """あなたはユーザーの質問をベクターストアまたはウェブ検索にルーティングする専門家です。
    ベクターストアにはエージェント、プロンプトエンジニアリング、アドバーサリアルアタックに関連する文書が含まれています。
    これらのトピックに関する質問にはベクターストアを使用し、それ以外の場合はウェブ検索を使用してください。"""
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}"),
        ]
    )

    question_router = route_prompt | structured_llm_router

    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        st.session_state.log += "---ROUTE QUESTION TO WEB SEARCH---" + "\n\n"
        st.session_state.placeholder.markdown("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        st.session_state.placeholder.markdown("ROUTE QUESTION TO RAG")
        st.session_state.log += "ROUTE QUESTION TO RAG" + "\n\n"
        return "vectorstore"

async def retrieve(state):
    st.session_state.status.update(label=f"**---RETRIEVE---**", state="running", expanded=True)
    st.session_state.placeholder.markdown(f"RETRIEVING…\n\nKEY WORD:{state['question']}")
    st.session_state.log += f"RETRIEVING…\n\nKEY WORD:{state['question']}" + "\n\n"

    embd = OpenAIEmbeddings()

    urls = [
        "https://lilianweng.github.io/posts/2023-06-23-agent/",
        "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
        "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
    ]

    docs = [WebBaseLoader(url).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)

    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embd,
    )
    retriever = vectorstore.as_retriever()

    question = state["question"]
    documents = retriever.invoke(question)
    st.session_state.placeholder.markdown("RETRIEVE SUCCESS!!")
    return {"documents": documents, "question": question}

async def web_search(state):
    st.session_state.status.update(label=f"**---WEB SEARCH---**", state="running", expanded=True)
    st.session_state.placeholder.markdown(f"WEB SEARCH…\n\nKEY WORD:{state['question']}")
    st.session_state.log += f"WEB SEARCH…\n\nKEY WORD:{state['question']}" + "\n\n"
    question = state["question"]
    web_search_tool = TavilySearchResults(k=3)

    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = Document(page_content=web_results)

    return {"documents": web_results, "question": question}

async def grade_documents(state):
    st.session_state.number_trial += 1
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=st.session_state.openai_api_key)
    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    system = """あなたは、ユーザーの質問に対して取得されたドキュメントの関連性を評価する採点者です。
ドキュメントにユーザーの質問に関連するキーワードや意味が含まれている場合、それを関連性があると評価してください。
目的は明らかに誤った取得を排除することです。厳密なテストである必要はありません。
ドキュメントが質問に関連しているかどうかを示すために、バイナリスコア「yes」または「no」を与えてください。"""
    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
        ]
    )

    retrieval_grader = grade_prompt | structured_llm_grader
    st.session_state.status.update(label=f"**---CHECK DOCUMENT RELEVANCE TO QUESTION---**", state="running", expanded=False)
    st.session_state.log += "**---CHECK DOCUMENT RELEVANCE TO QUESTION---**" + "\n\n"
    question = state["question"]
    documents = state["documents"]
    filtered_docs = []
    i = 0
    for d in documents:
        if st.session_state.number_trial <= 2:
            file_name = d.metadata["source"]
            file_name = os.path.basename(file_name.replace("\\","/"))
            i += 1
            score = retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            if grade == "yes":
                st.session_state.status.update(label=f"**---GRADE: DOCUMENT RELEVANT---**", state="running", expanded=True)
                st.session_state.placeholder.markdown(f"DOC {i}/{len(documents)} : **RELEVANT**\n\n")
                st.session_state.log += "---GRADE: DOCUMENT RELEVANT---" + "\n\n"
                st.session_state.log += f"doc {i}/{len(documents)} : RELEVANT\n\n"
                filtered_docs.append(d)
            else:
                st.session_state.status.update(label=f"**---GRADE: DOCUMENT NOT RELEVANT---**", state="error", expanded=True)
                st.session_state.placeholder.markdown(f"DOC {i}/{len(documents)} : **NOT RELEVANT**\n\n")
                st.session_state.log += "---GRADE: DOCUMENT NOT RELEVANT---" + "\n\n"
                st.session_state.log += f"DOC {i}/{len(documents)} : NOT RELEVANT\n\n"
        else:

            filtered_docs.append(d)

    if not st.session_state.number_trial <= 2:
        st.session_state.status.update(label=f"**---NO NEED TO CHECK---**", state="running", expanded=True)
        st.session_state.placeholder.markdown("QUERY TRANSFORMATION HAS BEEN COMPLETED")
        st.session_state.log += "QUERY TRANSFORMATION HAS BEEN COMPLETED" + "\n\n"

    return {"documents": filtered_docs, "question": question}

async def generate(state):
    st.session_state.status.update(label=f"**---GENERATE---**", state="running", expanded=False)
    st.session_state.log += "---GENERATE---" + "\n\n"
    prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """ユーザーから与えられたコンテキストを参考に質問に対し答えて下さい。"""),
                ("human", """Question: {question} 
Context: {context}"""),
            ]
        )
        
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=st.session_state.openai_api_key)

    rag_chain = prompt | llm | StrOutputParser()
    question = state["question"]
    documents = state["documents"]
    generation = rag_chain.invoke({"context": documents, "question": question})
    return {"documents": documents, "question": question, "generation": generation}


async def transform_query(state):
    st.session_state.status.update(label=f"**---TRANSFORM QUERY---**", state="running", expanded=True)
    st.session_state.placeholder.empty()
    st.session_state.log += "---TRANSFORM QUERY---" + "\n\n"
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=st.session_state.openai_api_key)

    system = """あなたは、入力された質問をベクトルストア検索に最適化されたより良いバージョンに変換する質問リライターです。
質問を見て、質問者の意図/意味について推論してより良いベクトル検索の為の質問を作成してください。"""
    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
            ),
        ]
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()
    question = state["question"]
    documents = state["documents"]
    better_question = question_rewriter.invoke({"question": question})
    st.session_state.log += f"better_question : {better_question}\n\n"
    st.session_state.placeholder.markdown(f"better_question : {better_question}")
    return {"documents": documents, "question": better_question}


async def decide_to_generate(state):
    filtered_documents = state["documents"]
    if not filtered_documents:
        st.session_state.status.update(label=f"**---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---**", state="error", expanded=False)
        st.session_state.log += "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---" + "\n\n"
        return "transform_query"                                     
    else:
        st.session_state.status.update(label=f"**---DECISION: GENERATE---**", state="running", expanded=False)
        st.session_state.log += "---DECISION: GENERATE---" + "\n\n"
        return "generate"

async def grade_generation_v_documents_and_question(state):
    st.session_state.number_trial += 1
    st.session_state.status.update(label=f"**---CHECK HALLUCINATIONS---**", state="running", expanded=False)
    st.session_state.log += "---CHECK HALLUCINATIONS---" + "\n\n"
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=st.session_state.openai_api_key)
    structured_llm_grader = llm.with_structured_output(GradeHallucinations)

    system = """あなたは、LLMの生成が取得された事実のセットに基づいているか/サポートされているかを評価する採点者です。
バイナリスコア「yes」または「no」を与えてください。「yes」は、回答が事実のセットに基づいている/サポートされていることを意味します。"""
    hallucination_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
        ]
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=st.session_state.openai_api_key)
    structured_llm_grader = llm.with_structured_output(GradeAnswer)

    system = """あなたは、回答が質問に対処しているか/解決しているかを評価する採点者です。
バイナリスコア「yes」または「no」を与えてください。「yes」は、回答が質問を解決していることを意味します。"""
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
        ]
    )

    answer_grader = answer_prompt | structured_llm_grader
    hallucination_grader = hallucination_prompt | structured_llm_grader
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]
    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score
    if st.session_state.number_trial <= 3:
        if grade == "yes":
            st.session_state.placeholder.markdown("DECISION: ANSWER IS BASED ON A SET OF FACTS")
            st.session_state.log += "---DECISION: ANSWER IS BASED ON A SET OF FACTS---" + "\n\n"
            st.session_state.log += "---GRADE GENERATION vs QUESTION---" + "\n\n"
            score = answer_grader.invoke({"question": question, "generation": generation})
            grade = score.binary_score
            st.session_state.status.update(label=f"**---GRADE GENERATION vs QUESTION---**", state="running", expanded=True)
            if grade == "yes":
                st.session_state.status.update(label=f"**---DECISION: GENERATION ADDRESSES QUESTION---**", state="running", expanded=True)
                with st.session_state.placeholder:
                    st.markdown("**USEFUL!!**")
                    st.markdown(f"question : {question}")
                    st.markdown(f"generation : {generation}")                   
                    st.session_state.log += "---DECISION: GENERATION ADDRESSES QUESTION---" + "\n\n"
                    st.session_state.log += f"USEFUL!!\n\n"
                    st.session_state.log += f"question:{question}\n\n"
                    st.session_state.log += f"generation:{generation}\n\n"
                return "useful"
            else:
                st.session_state.number_trial -= 1
                st.session_state.status.update(label=f"**---DECISION: GENERATION DOES NOT ADDRESS QUESTION---**", state="error", expanded=True)
                with st.session_state.placeholder:
                    st.markdown("**NOT USEFUL**")
                    st.markdown(f"question:{question}")
                    st.markdown(f"generation:{generation}")
                    st.session_state.log += "---DECISION: GENERATION DOES NOT ADDRESS QUESTION---" + "\n\n"
                    st.session_state.log += f"NOT USEFUL\n\n"
                    st.session_state.log += f"question:{question}\n\n"
                    st.session_state.log += f"generation:{generation}\n\n"
                return "not useful"
        else:
            st.session_state.status.update(label=f"**---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---**", state="error", expanded=True)
            with st.session_state.placeholder:
                st.markdown("not grounded")
                st.markdown(f"question:{question}")
                st.markdown(f"generation:{generation}")
                st.session_state.log += "---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---" + "\n\n"
                st.session_state.log += f"not grounded\n\n"
                st.session_state.log += f"question:{question}\n\n"
                st.session_state.log += f"generation:{generation}\n\n"
            return "not supported"
    else:
        st.session_state.status.update(label=f"**---NO NEED TO CHECK---**", state="running", expanded=True)
        st.session_state.placeholder.markdown("TRIAL LIMIT EXCEEDED")
        st.session_state.log += "---NO NEED TO CHECK---" + "\n\n"
        st.session_state.log += "TRIAL LIMIT EXCEEDED" + "\n\n"
        return "useful"

async def run_workflow(inputs):
    st.session_state.number_trial = 0
    with st.status(label="**GO!!**", expanded=True,state="running") as st.session_state.status:
        st.session_state.placeholder = st.empty()
        value = await st.session_state.workflow.ainvoke(inputs)

    st.session_state.placeholder.empty()
    st.session_state.message_placeholder = st.empty()
    st.session_state.status.update(label="**FINISH!!**", state="complete", expanded=False)
    st.session_state.message_placeholder.markdown(value["generation"])
    with st.popover("ログ"):
        st.markdown(st.session_state.log)

def st_rag_langgraph():

    if 'log' not in st.session_state:
        st.session_state.log = ""

    if 'status_container' not in st.session_state:
        st.session_state.status_container = st.empty()

    if not hasattr(st.session_state, "workflow"):

        workflow = StateGraph(GraphState)

        workflow.add_node("web_search", web_search)
        workflow.add_node("retrieve", retrieve)
        workflow.add_node("grade_documents", grade_documents)
        workflow.add_node("generate", generate)
        workflow.add_node("transform_query", transform_query)

        workflow.add_conditional_edges(
            START,
            route_question,
            {
                "vectorstore": "retrieve",
                "web_search": "web_search",
            },
        )
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            grade_generation_v_documents_and_question,
            {
                "not supported": "generate",
                "useful": END,
                "not useful": "transform_query",
            },
        )

        app = workflow.compile()
        app = app.with_config(recursion_limit=10,run_name="Agent",tags=["Agent"])
        app.name = "Agent"
        st.session_state.workflow = app


    st.title("Adaptive RAG by LangGraph")

    if prompt := st.chat_input("質問を入力してください"):
        if not st.session_state.openai_api_key or not st.session_state.tavily_api_key:
            sac.alert(label='warning', description='Please add your OpenAI API key and Tavily API key to continue.', color='red', banner=[False, True], icon=True, size='lg')
            st.stop()
        st.session_state.log = ""
        with st.chat_message("user", avatar="😊"):
            st.markdown(prompt)

        inputs = {"question": prompt}
        asyncio.run(run_workflow(inputs))

if __name__ == "__main__":
    st_rag_langgraph()