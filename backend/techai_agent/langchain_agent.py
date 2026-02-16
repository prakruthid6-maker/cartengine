"""
LangChain-based conversational AI agent for e-commerce.

Features:
- Conversation memory with sliding window
- Tool orchestration with ReAct pattern
- Personalized recommendations based on context
- Integration with existing product tools
"""

import os
from typing import Optional, List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# ============ LLM Configuration ============

def get_llm(model_name: str = "gemini-2.0-flash") -> ChatGoogleGenerativeAI:
    """Get the LangChain LLM instance."""
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
        convert_system_message_to_human=True,
    )


# ============ Memory Configuration ============

class ConversationManager:
    """Manages conversation memory and context per user session."""
    
    def __init__(self, k: int = 10):
        """
        Initialize with sliding window size.
        
        Args:
            k: Number of recent messages to keep in memory
        """
        self._sessions: Dict[str, ConversationBufferWindowMemory] = {}
        self.k = k
    
    def get_memory(self, session_id: str) -> ConversationBufferWindowMemory:
        """Get or create memory for a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationBufferWindowMemory(
                k=self.k,
                memory_key="chat_history",
                return_messages=True,
                input_key="input",
                output_key="output"
            )
        return self._sessions[session_id]
    
    def clear_session(self, session_id: str) -> None:
        """Clear memory for a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_context_summary(self, session_id: str) -> str:
        """Get a summary of the conversation context."""
        memory = self.get_memory(session_id)
        messages = memory.chat_memory.messages
        if not messages:
            return "No previous context."
        return f"Previous {len(messages)} messages in conversation."


# Global conversation manager
conversation_manager = ConversationManager(k=10)


# ============ Agent Prompt ============

REACT_PROMPT = """You are an intelligent e-commerce AI assistant for ShopAI. You help customers find products, track orders, get recommendations, and answer questions about the store.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Important guidelines:
1. Be friendly, helpful, and conversational
2. When showing products, format them nicely with names, prices, and ratings
3. If you don't have enough information, ask clarifying questions
4. For order tracking, always confirm the order ID with the user
5. Provide personalized recommendations based on the conversation history
6. Use emojis sparingly to make responses engaging

Previous conversation:
{chat_history}

Question: {input}
{agent_scratchpad}"""

AGENT_PROMPT = PromptTemplate.from_template(REACT_PROMPT)


# ============ Tool Wrappers ============

def create_product_tools(product_service) -> List[Tool]:
    """Create LangChain tools from the product service."""
    
    async def search_products_wrapper(query: str) -> str:
        """Search for products matching the query."""
        try:
            products = await product_service.get_products_by_query(f"SELECT * FROM c")
            # Filter locally for simplicity
            query_lower = query.lower()
            filtered = [p for p in products if query_lower in p.name.lower() or query_lower in p.description.lower()]
            
            if not filtered:
                return f"No products found matching '{query}'."
            
            result = f"Found {len(filtered)} products:\n\n"
            for p in filtered[:5]:  # Limit to 5 results
                result += f"📦 **{p.name}** - ${p.price:.2f}\n"
                result += f"   ⭐ {p.ratings}/5 ({p.reviews} reviews)\n"
                result += f"   {p.description[:100]}...\n\n"
            return result
        except Exception as e:
            return f"Error searching products: {str(e)}"
    
    async def get_product_categories_wrapper(_: str) -> str:
        """Get all available product categories."""
        try:
            products = await product_service.get_products_by_query("SELECT * FROM c")
            categories = list(set(p.categoryId for p in products))
            return f"Available categories: {', '.join(categories)}"
        except Exception as e:
            return f"Error getting categories: {str(e)}"
    
    async def get_deals_wrapper(_: str) -> str:
        """Get products on sale or with special badges."""
        try:
            products = await product_service.get_products_by_query("SELECT * FROM c")
            deals = [p for p in products if p.badge == 'Sale']
            
            if not deals:
                return "No products currently on sale."
            
            result = "🏷️ **Current Deals:**\n\n"
            for p in deals[:5]:
                result += f"🔥 **{p.name}** - ${p.price:.2f} (SALE!)\n"
            return result
        except Exception as e:
            return f"Error getting deals: {str(e)}"
    
    async def get_top_rated_wrapper(_: str) -> str:
        """Get top-rated products."""
        try:
            products = await product_service.get_products_by_query("SELECT * FROM c")
            sorted_products = sorted(products, key=lambda p: p.ratings, reverse=True)
            
            result = "⭐ **Top Rated Products:**\n\n"
            for p in sorted_products[:5]:
                result += f"🏆 **{p.name}** - ${p.price:.2f}\n"
                result += f"   ⭐ {p.ratings}/5 ({p.reviews} reviews)\n\n"
            return result
        except Exception as e:
            return f"Error getting top rated products: {str(e)}"
    
    def sync_wrapper(async_func):
        """Wrapper to make async functions work synchronously."""
        import asyncio
        def wrapper(input_str: str) -> str:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(async_func(input_str))
            finally:
                loop.close()
        return wrapper
    
    return [
        Tool(
            name="search_products",
            func=sync_wrapper(search_products_wrapper),
            coroutine=search_products_wrapper,
            description="Search for products by name, category, or description. Input should be a search query string."
        ),
        Tool(
            name="get_categories",
            func=sync_wrapper(get_product_categories_wrapper),
            coroutine=get_product_categories_wrapper,
            description="Get all available product categories. No input required, just pass an empty string."
        ),
        Tool(
            name="get_deals",
            func=sync_wrapper(get_deals_wrapper),
            coroutine=get_deals_wrapper,
            description="Get products currently on sale or with special offers. No input required, just pass an empty string."
        ),
        Tool(
            name="get_top_rated",
            func=sync_wrapper(get_top_rated_wrapper),
            coroutine=get_top_rated_wrapper,
            description="Get the top-rated products based on customer reviews. No input required, just pass an empty string."
        ),
    ]


# ============ Chat Agent ============

class ChatAgent:
    """LangChain-powered chat agent for the e-commerce platform."""
    
    def __init__(self, product_service=None):
        self.llm = get_llm()
        self.product_service = product_service
        self.tools = []
        
        # Add product tools if service is available
        if product_service:
            self.tools.extend(create_product_tools(product_service))
        
        # Create the agent if tools are available
        if self.tools:
            self.agent = create_react_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=AGENT_PROMPT
            )
        else:
            self.agent = None
    
    async def chat(
        self,
        message: str,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Process a chat message and return a response.
        
        Args:
            message: The user's message
            session_id: Unique session identifier for memory
            user_id: Optional user ID for personalization
        
        Returns:
            The assistant's response
        """
        memory = conversation_manager.get_memory(session_id)
        
        if self.agent and self.tools:
            # Use the full agent with tools
            executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5
            )
            
            try:
                result = await executor.ainvoke({
                    "input": message,
                    "chat_history": memory.chat_memory.messages
                })
                return result.get("output", "I'm sorry, I couldn't process that request.")
            except Exception as e:
                return f"I encountered an error: {str(e)}. Please try again."
        else:
            # Fallback to direct LLM call
            context = ""
            if memory.chat_memory.messages:
                context = "Previous conversation:\n"
                for msg in memory.chat_memory.messages[-6:]:
                    role = "User" if msg.type == "human" else "Assistant"
                    context += f"{role}: {msg.content}\n"
            
            prompt = f"""You are a helpful e-commerce AI assistant for ShopAI.

{context}

User: {message}

Respond helpfully and conversationally. If the user asks about products, let them know you can help search once products are loaded."""

            try:
                response = await self.llm.ainvoke(prompt)
                # Save to memory
                memory.save_context({"input": message}, {"output": response.content})
                return response.content
            except Exception as e:
                return f"I'm having trouble responding right now: {str(e)}"
    
    def clear_memory(self, session_id: str) -> None:
        """Clear conversation memory for a session."""
        conversation_manager.clear_session(session_id)
