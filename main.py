#!/usr/bin/env python3
"""
Select From My Ideas - CLI Interface

Transform raw, unstructured ideas into concrete, actionable outcomes
through intelligent multi-turn conversations.
"""

import sys
from typing import Optional

from models import UserSelection, MainAgentOutput, FinalOutput
from services.orchestrator import Orchestrator


def print_header():
    """Print the application header."""
    print("\n" + "=" * 60)
    print("  Select From My Ideas")
    print("  Transform your ideas into action")
    print("=" * 60 + "\n")


def print_summary(summary: str):
    """Print the agent's summary."""
    print("\n" + "-" * 40)
    print(summary)
    print("-" * 40 + "\n")


def print_selections(output: MainAgentOutput) -> list[UserSelection]:
    """Display selections and get user input."""
    selections = []

    for i, selection in enumerate(output.selections, 1):
        print(f"\n[Question {i}] {selection.question}\n")

        for j, option in enumerate(selection.options, 1):
            print(f"  {j}. {option}")

        if selection.allow_other:
            print(f"  {len(selection.options) + 1}. Other (enter your own)")

        while True:
            try:
                choice = input("\nYour choice (number): ").strip()

                if not choice:
                    print("Please enter a number.")
                    continue

                choice_num = int(choice)
                max_choice = len(selection.options) + (1 if selection.allow_other else 0)

                if 1 <= choice_num <= len(selection.options):
                    # Selected a predefined option
                    selected = UserSelection(
                        question=selection.question,
                        selected_option=selection.options[choice_num - 1],
                    )
                    selections.append(selected)
                    print(f"  -> {selection.options[choice_num - 1]}")
                    break
                elif selection.allow_other and choice_num == len(selection.options) + 1:
                    # Selected "Other"
                    custom = input("Enter your own answer: ").strip()
                    selected = UserSelection(
                        question=selection.question,
                        custom_input=custom,
                    )
                    selections.append(selected)
                    print(f"  -> {custom}")
                    break
                else:
                    print(f"Please enter a number between 1 and {max_choice}.")

            except ValueError:
                print("Please enter a valid number.")

    return selections


def print_final_output(output: FinalOutput):
    """Display the final synthesized output."""
    print("\n" + "=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)

    print(f"\n## Summary\n{output.final_summary}")

    print("\n## Action Items")
    for i, item in enumerate(output.action_items, 1):
        priority_emoji = {"high": "[!]", "medium": "[+]", "low": "[-]"}
        effort_label = {"minimal": "Easy", "moderate": "Medium", "significant": "Hard"}
        print(
            f"  {i}. {priority_emoji.get(item.priority, '')} {item.action}"
            f" ({effort_label.get(item.effort, item.effort)})"
        )

    print("\n## Tips")
    for tip in output.tips:
        print(f"  - {tip}")

    print("\n## Insights")
    for insight in output.insights:
        print(f"  - {insight}")

    print(f"\n## Next Steps\n{output.next_steps}")

    print(f"\n## Encouragement\n{output.encouragement}")

    print("\n" + "=" * 60 + "\n")


def main():
    """Main CLI loop."""
    print_header()

    # Get initial idea from user
    print("What's your idea? (Enter your raw thoughts, then press Enter)\n")
    print("Example: I want to start exercising but don't know where to begin")
    print("Example: 운동을 시작하고 싶은데 어떻게 해야 할지 모르겠어요\n")

    user_input = input("> ").strip()

    if not user_input:
        print("No input provided. Exiting.")
        sys.exit(0)

    try:
        orchestrator = Orchestrator()
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please create a .env file with OPENAI_API_KEY=your-key-here")
        sys.exit(1)

    print("\nThinking...")

    try:
        # Start the session
        output = orchestrator.start_session(user_input)
        round_num = 1

        # Main conversation loop
        while True:
            print(f"\n[Round {round_num}]")
            print_summary(output.summary)

            if output.should_conclude:
                print("Generating final output...")
                # Process empty selections to trigger conclusion
                final = orchestrator.process_selections([])
                if isinstance(final, FinalOutput):
                    print_final_output(final)
                break

            if not output.selections:
                print("No more questions. Generating final output...")
                final = orchestrator.process_selections([])
                if isinstance(final, FinalOutput):
                    print_final_output(final)
                break

            # Get user selections
            selections = print_selections(output)

            print("\nThinking...")

            # Process selections
            result = orchestrator.process_selections(selections)

            if isinstance(result, FinalOutput):
                print_final_output(result)
                break
            else:
                output = result
                round_num += 1

    except KeyboardInterrupt:
        print("\n\nSession interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
