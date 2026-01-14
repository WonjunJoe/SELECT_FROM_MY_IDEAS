#!/usr/bin/env python3
"""
Select From My Ideas - CLI Interface

Transform raw, unstructured ideas into concrete, actionable outcomes
through intelligent multi-turn conversations.
"""

import sys

from config import settings
from models import UserSelection, MainAgentOutput, FinalOutput
from services.orchestrator import Orchestrator
from core.logging import logger, setup_logging


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


def print_selections(output: MainAgentOutput) -> tuple[list[UserSelection], bool]:
    """Display selections and get user input.

    Returns:
        Tuple of (selections list, early_exit flag)
    """
    selections = []

    for i, selection in enumerate(output.selections, 1):
        print(f"\n[Question {i}] {selection.question}\n")

        for j, option in enumerate(selection.options, 1):
            print(f"  {j}. {option}")

        if selection.allow_other:
            print(f"  {len(selection.options) + 1}. Other (enter your own)")

        print("\n  (Type 'done' to finish early and get your results)")

        while True:
            try:
                choice = input("\nYour choice (number or 'done'): ").strip().lower()

                if not choice:
                    print("Please enter a number.")
                    continue

                # Check for early exit
                if choice in ('done', 'q', 'quit', 'end'):
                    logger.info("User requested early exit")
                    return selections, True

                choice_num = int(choice)
                max_choice = len(selection.options) + (1 if selection.allow_other else 0)

                if 1 <= choice_num <= len(selection.options):
                    # Selected a predefined option
                    selected = UserSelection(
                        question=selection.question,
                        selected_option=selection.options[choice_num - 1],
                    )
                    selections.append(selected)
                    logger.debug(
                        f"User selected option {choice_num}",
                        question=selection.question[:50],
                        selected=selection.options[choice_num - 1],
                    )
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
                    logger.debug(
                        f"User entered custom input",
                        question=selection.question[:50],
                        custom_input=custom,
                    )
                    print(f"  -> {custom}")
                    break
                else:
                    print(f"Please enter a number between 1 and {max_choice}.")

            except ValueError:
                print("Please enter a valid number or 'done' to finish early.")

    return selections, False


def print_final_output(output: FinalOutput):
    """Display the final synthesized output."""
    print("\n" + "=" * 60)
    print("  FINAL RESULTS")
    print("=" * 60)

    # Display user's original input
    print(f"\n## Your Query\n{output.original_input}")

    # Display user profile if available
    if output.user_profile:
        print("\n## Your Profile")
        profile = output.user_profile
        print(f"  Age: {profile.age}")
        print(f"  Gender: {profile.gender}")
        print(f"  Interests: {', '.join(profile.interests)}")
        if profile.job:
            print(f"  Job: {profile.job}")
        if profile.lifestyle:
            print(f"  Lifestyle: {profile.lifestyle}")
        if profile.goals:
            print(f"  Goals: {profile.goals}")

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
    # Initialize logging from config (console disabled for CLI by default)
    setup_logging(
        level=settings.log_level,
        log_to_file=settings.log_to_file,
        log_to_console=False,  # Disable console for CLI to avoid cluttering output
    )

    logger.info("CLI application started")

    print_header()

    # Get initial idea from user
    print("What's your idea? (Enter your raw thoughts, then press Enter)\n")
    print("Example: I want to start exercising but don't know where to begin")
    print("Example: 운동을 시작하고 싶은데 어떻게 해야 할지 모르겠어요\n")

    user_input = input("> ").strip()

    if not user_input:
        logger.info("No input provided, exiting")
        print("No input provided. Exiting.")
        sys.exit(0)

    logger.info(f"User input received", input_length=len(user_input))

    try:
        orchestrator = Orchestrator()
    except ValueError as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        print(f"\nError: {e}")
        print("Please create a .env file with OPENAI_API_KEY=your-key-here")
        sys.exit(1)

    print("\nThinking...")

    try:
        # Start the session
        logger.info("Starting session")
        output = orchestrator.start_session(user_input)
        round_num = 1

        # Main conversation loop
        while True:
            logger.info(f"Round {round_num} started")
            print(f"\n[Round {round_num}]")
            print_summary(output.summary)

            if output.should_conclude:
                logger.info("Session concluding")
                print("Generating final output...")
                # Process empty selections to trigger conclusion
                final = orchestrator.process_selections([])
                if isinstance(final, FinalOutput):
                    logger.info(
                        "Final output generated",
                        num_action_items=len(final.action_items),
                    )
                    print_final_output(final)
                break

            if not output.selections:
                logger.info("No more selections, concluding")
                print("No more questions. Generating final output...")
                final = orchestrator.process_selections([])
                if isinstance(final, FinalOutput):
                    logger.info(
                        "Final output generated",
                        num_action_items=len(final.action_items),
                    )
                    print_final_output(final)
                break

            # Get user selections
            selections, early_exit = print_selections(output)

            # Handle early exit
            if early_exit:
                print("\nEnding early. Generating your results...")
                final = orchestrator.force_conclude()
                logger.info(
                    "Early exit - final output generated",
                    num_action_items=len(final.action_items),
                )
                print_final_output(final)
                break

            print("\nThinking...")

            # Process selections
            logger.info(f"Processing {len(selections)} selections")
            result = orchestrator.process_selections(selections)

            if isinstance(result, FinalOutput):
                logger.info(
                    "Final output generated",
                    num_action_items=len(result.action_items),
                )
                print_final_output(result)
                break
            else:
                output = result
                round_num += 1

    except KeyboardInterrupt:
        logger.info("Session interrupted by user")
        print("\n\nSession interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Error during session: {e}")
        print(f"\nError: {e}")
        sys.exit(1)

    logger.info("CLI application finished")


if __name__ == "__main__":
    main()
