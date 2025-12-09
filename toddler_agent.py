import os
import sys
import datetime
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from ddgs import DDGS
from colorama import Fore, Style, init

# Initialize colorama for pretty printing
init(autoreset=True)

class ToddlerBrain:
    def __init__(self, api_key=None):
        """
        Initializes the Brain (Gemini).
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        # --- PASTE YOUR KEY BELOW IF HARDCODING ---
        # self.api_key = "AIzaSy..." 
        
        if not self.api_key:
            print(f"{Fore.RED}Error: Gemini API Key is missing.")
            print(f"{Fore.YELLOW}Please set the GEMINI_API_KEY environment variable.")
            sys.exit(1)
            
        genai.configure(api_key=self.api_key)
        
        # [GUARDRAIL - 2025-12-09] - Configure Safety Settings
        # Setting all safety thresholds to BLOCK_LOW_AND_ABOVE to ensure 
        # the model refuses to generate hate speech, sexual content, or dangerous content.
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }

        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=self.safety_settings
        )

    # [GUARDRAIL - 2025-12-09] - New method to interpret toddler speech and check safety
    def interpret_input(self, user_input):
        """
        Uses the LLM to fix mispronunciations and check if the topic is safe
        BEFORE performing any search.
        """
        print(f"{Style.DIM}* Brain is checking if this question is safe and clear... *")
        
        guardrail_prompt = (
            "You are a safety filter and translator for a toddler. "
            f"The user input is: '{user_input}'. "
            "1. Correct any mispronunciations or toddler-speak (e.g., 'wawa' -> 'water'). "
            "2. If the topic is inappropriate for a 3-year-old (violence, adult topics, scary things), return exactly: UNSAFE. "
            "3. If safe, return only the corrected simple question."
        )

        try:
            response = self.model.generate_content(guardrail_prompt)
            # Check if the response was blocked by safety filters
            if not response.text: 
                return "UNSAFE"
            cleaned_text = response.text.strip()
            return cleaned_text
        except Exception as e:
            # This often happens if the model refuses to answer due to safety settings
            print(f"{Fore.RED}Guardrail Check Blocked/Failed: {e}")
            return "UNSAFE" 

    def think_and_simplify(self, question, context):
        """
        Takes a question and context, and generates a simple explanation.
        """
        print(f"{Style.DIM}* Brain is thinking about how to explain this... *")

        # [GUARDRAIL - 2025-12-09] - Updated System Instruction
        # Added explicit instructions to avoid scary topics and maintain a gentle tone.
        system_instruction = (
            "You are a gentle, wise, and enthusiastic teacher talking to a 3-year-old toddler. "
            "Your goal is to satisfy their curiosity. "
            "Use very simple words, analogies involving toys, animals, or snacks, and a warm tone. "
            "Keep the answer short (2-3 sentences max). "
            "Do not use jargon. "
            "Use the provided context to answer the question truthfully. "
            "CRITICAL SAFETY RULE: If the context contains anything violent, scary, or adult, "
            "ignore it and provide a happy, safe, generic answer about the topic."
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
        print(f"{Style.DIM}* Hands are looking up '{query}' on the internet... *")
        
        try:
            # [GUARDRAIL - 2025-12-09] - Fixed SafeSearch Parameter
            # Changed 'strict' to 'on' because DDGS uses 'on', 'moderate', or 'off'.
            results = self.ddgs.text(query, max_results=3, safesearch='on')
            
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
        print(f"{Fore.CYAN}User: ", end="")
        return input().strip()

    def run(self):
        """Main interaction loop connecting Brain and Hands."""
        print(f"{Fore.YELLOW}=== Curious Toddler Bot (SafeGuard Edition) Started ===")
        print("Ask me a 'why' question! (e.g., 'Why is the sky blue?')")

        while True:
            user_input = self.listen()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{Fore.YELLOW}Bye bye! Stay curious!")
                break

            if not user_input:
                continue
            
            # [GUARDRAIL - 2025-12-09] - Pre-processing Step
            # 1. Interpret and Sanitize Input BEFORE calculating logic or searching
            cleaned_query = self.brain.interpret_input(user_input)

            # [GUARDRAIL - 2025-12-09] - Safety Block
            if cleaned_query == "UNSAFE":
                print(f"\n{Fore.BLUE}Bot:{Style.RESET_ALL} I think we should ask a grown-up about that! Let's talk about something happy, like puppies or rainbows!\n")
                continue

            print(f"{Fore.MAGENTA}(I heard: '{cleaned_query}')")

            # Detect if it's a statement that needs a "Why?" appended
            question_words = ['why', 'how', 'what', 'when', 'who', 'where']
            is_question = any(cleaned_query.lower().startswith(w) for w in question_words) or cleaned_query.endswith('?')
            
            final_query = cleaned_query
            if not is_question:
                final_query = f"Why {cleaned_query}?"

            # 2. Use Hands to find info (With SafeSearch)
            search_results = self.hands.search_internet(final_query)
            
            if not search_results:
                print(f"{Fore.RED}I couldn't find anything about that online. Maybe try asking differently?")
                continue

            # 3. Use Brain to process info (With Safety Settings)
            answer = self.brain.think_and_simplify(final_query, search_results)

            # 4. Speak
            print(f"\n{Fore.BLUE}Bot:{Style.RESET_ALL} {answer}\n")

if __name__ == "__main__":
    try:
        agent = CuriousToddlerAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\nSee you later!")