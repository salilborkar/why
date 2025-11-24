import os
import sys
import google.generativeai as genai
from ddgs import DDGS
from colorama import Fore, Style, init

# Initialize colorama for pretty printing
init(autoreset=True)

class ToddlerBrain:
    def __init__(self, api_key=None):
        """
        Initializes the Brain (Gemini).
        """
        # Try to get key from argument or environment variable
        #self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # --- PASTE YOUR KEY BELOW IF YOU WANT TO HARDCODE IT ---
        self.api_key = "AIzaSyBMBxwX8QoTFCKgJoO6ueeZQhLiDMLtQG0" 
        
        if not self.api_key:
            print(f"{Fore.RED}Error: Gemini API Key is missing.")
            print(f"{Fore.YELLOW}Please set the GEMINI_API_KEY environment variable.")
            sys.exit(1)
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def think_and_simplify(self, question, context):
        """
        Takes a question and context, and generates a simple explanation.
        """
        # FIX: Changed Fore.DIM to Style.DIM
        print(f"{Style.DIM}* Brain is thinking about how to explain this... *")

        system_instruction = (
            "You are a gentle, wise, and enthusiastic teacher talking to a 3-year-old toddler. "
            "Your goal is to satisfy their curiosity. "
            "Use very simple words, analogies involving toys, animals, or snacks, and a warm tone. "
            "Keep the answer short (2-3 sentences max). "
            "Do not use jargon. "
            "Use the provided context to answer the question truthfully."
        )

        prompt = f"{system_instruction}\n\nThe toddler asks: '{question}'\n\nHere is what the internet says (Context):\n{context}"

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Oh no! My brain got a little stuck: {e}"

class ToddlerHands:
    def __init__(self):
        """
        Initializes the Hands (Search Tools).
        """
        self.ddgs = DDGS()

    def search_internet(self, query):
        """
        Uses 'hands' to go out and fetch information from the internet.
        """
        # FIX: Changed Fore.DIM to Style.DIM
        print(f"{Style.DIM}* Hands are looking up '{query}' on the internet... *")
        
        try:
            # simple search for text results
            results = self.ddgs.text(query, max_results=3)
            
            if not results:
                return None

            # Combine the snippets into one context string
            context = "\n".join([f"- {r['body']}" for r in results])
            return context
            
        except Exception as e:
            print(f"{Fore.RED}Search failed: {e}")
            return None

class CuriousToddlerAgent:
    def __init__(self):
        self.brain = ToddlerBrain()
        self.hands = ToddlerHands()

    def listen(self):
        """Listening for user input."""
        print(f"\n{Fore.GREEN}Toddler Bot is listening... (Type 'exit' to quit)")
        print(f"{Fore.CYAN}Toddler: ", end="")
        return input().strip()

    def run(self):
        """Main interaction loop connecting Brain and Hands."""
        print(f"{Fore.YELLOW}=== Curious Toddler Bot (Fixed Edition) Started ===")
        print("Ask me a 'why' question! (e.g., 'Why is the sky blue?')")

        while True:
            user_input = self.listen()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{Fore.YELLOW}Bye bye! Stay curious!")
                break

            if not user_input:
                continue

            # Detect if it's a statement that needs a "Why?" appended
            question_words = ['why', 'how', 'what', 'when', 'who', 'where']
            is_question = any(user_input.lower().startswith(w) for w in question_words) or user_input.endswith('?')
            
            final_query = user_input
            if not is_question:
                print(f"{Fore.MAGENTA}(Adding 'Why?' to your statement...)")
                final_query = f"Why {user_input}?"

            # 1. Use Hands to find info
            search_results = self.hands.search_internet(final_query)
            
            if not search_results:
                print(f"{Fore.RED}I couldn't find anything about that online. Maybe try asking differently?")
                continue

            # 2. Use Brain to process info
            answer = self.brain.think_and_simplify(final_query, search_results)

            # 3. Speak
            print(f"\n{Fore.BLUE}Bot:{Style.RESET_ALL} {answer}\n")

if __name__ == "__main__":
    try:
        agent = CuriousToddlerAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\nSee you later!")