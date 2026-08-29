import sys
import io
import os

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from setux_bot.engine import SetuXBotEngine

console = Console()

LANGUAGES = {
    "1": "English",
    "2": "Hindi (हिंदी)",
    "3": "Marathi (मराठी)",
    "4": "Bengali (বাংলা)",
    "5": "Tamil (தமிழ்)",
    "6": "Telugu (తెలుగు)",
    "7": "Gujarati (ગુજરાતી)"
}

def main():
    engine = SetuXBotEngine()
    
    # Check Ollama connection
    if not engine.ollama.is_server_online():
        console.print("[bold red][!] Warning: Could not connect to local Ollama server at http://127.0.0.1:11434[/bold red]")
        console.print("[yellow]Please ensure 'ollama serve' is running in the background.[/yellow]\n")
    else:
        console.print(f"[bold green][✓] SetuX AI Bot Ready ([white]{engine.ollama.model_name}[/white])[/bold green]\n")

    current_language = "English"

    while True:
        try:
            user_input = Prompt.ask(f"[bold bold_cyan]SetuX User ({current_language})[/bold bold_cyan]").strip()
            
            if not user_input:
                continue

            # Command Handling
            if user_input.lower() in ["/exit", "exit", "quit", "/quit"]:
                console.print("\n[bold cyan]Goodbye![/bold cyan]\n")
                break

            elif user_input.lower() == "/help":
                console.print(Panel(
                    "• Ask any question about updating Aadhaar, PAN Card, Ration Card, Voter ID, Driving License on SetuX.\n"
                    "• The AI Bot will reply in the language you ask in.\n"
                    "• Type /model to switch between 7.6B (Best Accuracy) and 1.5B (Speed).\n"
                    "• Type /clear to start a fresh chat session.",
                    title="Help & Commands", border_style="yellow"
                ))
                continue

            elif user_input.lower() == "/clear":
                engine.clear_history()
                console.print("[green][✓] Conversation history cleared.[/green]\n")
                continue

            elif user_input.lower() == "/status":
                online = engine.ollama.is_server_online()
                models = engine.ollama.get_available_models()
                console.print(f"Ollama Server Online: [bold]{online}[/bold]")
                console.print(f"Active Model: [bold]{engine.ollama.model_name}[/bold]")
                console.print(f"Available Models: {models}\n")
                continue

            elif user_input.lower() == "/model":
                available = engine.ollama.get_available_models()
                console.print(f"\nCurrently Active Model: [bold yellow]{engine.ollama.model_name}[/bold yellow]")
                console.print("Available Installed Models:")
                for idx, m in enumerate(available, 1):
                    console.print(f"  [{idx}] {m}")
                choice = Prompt.ask("Select model number", choices=[str(i) for i in range(1, len(available) + 1)])
                selected_model = available[int(choice) - 1]
                engine = SetuXBotEngine(model_name=selected_model)
                console.print(f"[bold green][✓] Switched model to {selected_model}[/bold green]\n")
                continue

            elif user_input.lower() == "/lang":
                console.print("\nSelect Preferred Language:")
                for k, v in LANGUAGES.items():
                    console.print(f"  [{k}] {v}")
                choice = Prompt.ask("Enter number", choices=list(LANGUAGES.keys()), default="1")
                current_language = LANGUAGES[choice].split(" ")[0]
                console.print(f"[green][✓] Preferred language set to {current_language}[/green]\n")
                continue

            # Real-Time Streaming Response
            console.print("[bold green]SetuX AI:[/bold green] ", end="")
            token_gen, is_allowed = engine.process_query_stream(user_input, target_language=current_language)

            for token in token_gen:
                sys.stdout.write(token)
                sys.stdout.flush()
            print("\n")

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Goodbye![/bold cyan]\n")
            break
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]\n")

if __name__ == "__main__":
    main()
