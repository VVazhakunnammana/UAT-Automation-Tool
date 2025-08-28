import pytest
from playwright.sync_api import Page
from pages.grading_page import GradingPage
from datetime import datetime

def load_test_data_from_excel():
    """
    Load test data from an Excel file
    """
    grading_page = GradingPage(Page)
    mentor_config_file = r"C:\Users\VVazhakunnamMana\Documents\TestData\UAT_TestData.xlsx"
    mentors = grading_page.read_mentor_configurations(mentor_config_file)
    print("Mentors loaded:" + str(mentors))

    return mentors

@pytest.mark.parametrize("state_name, mentor_url", load_test_data_from_excel())
def test_mentor_api_excel(grading_page: GradingPage, state_name, mentor_url):
    """
    Main function that orchestrates multi-mentor processing
    """
    print("="*80)
    print("MULTI-MENTOR PROCESSING SYSTEM")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    # File paths
    mentor_config_file = r"C:\Users\VVazhakunnamMana\Documents\TestData\UAT_TestData.xlsx"
    questions_file = r"C:\Users\VVazhakunnamMana\Documents\TestData\UAT_TestData.xlsx"

    # Read mentor configurations
    print("\n1. Reading mentor configurations...")
    mentors = grading_page.read_mentor_configurations(mentor_config_file)

    
    print("Mentors loaded:"+ str(mentors))

    if not mentors:
        print("No mentors found to process. Exiting.")
        return

    # Read questions from template
    print("\n2. Reading questions from template...")
    questions = grading_page.read_questions_from_template(questions_file)

    if not questions:
        print("No questions found to process. Exiting.")
        return
    
    # Process each mentor
    total_processed = 0
    total_failed = 0
    successful_mentors = []
    failed_mentors = []
    
    
    print(f"\n{'='*80}")
    # print(f"[{idx}/{len(mentors)}] PROCESSING MENTOR {idx} OF {len(mentors)}")
    print(f"{'='*80}")
    
    try:
        processed, failed =  grading_page.process_mentor_questions(
            mentor_url, state_name, questions, model=None
        )
        
        total_processed += processed
        total_failed += failed

        if failed == 0:
            successful_mentors.append(state_name)
        else:
            failed_mentors.append(f"{state_name} ({failed} failures)")
            
    except Exception as e:
        print(f"Failed to process mentor {state_name}: {str(e)}")
        failed_mentors.append(f"{state_name} (complete failure)")
        total_failed += len(questions)
    
    # Final summary
    print(f"\n{'='*80}")
    print("MULTI-MENTOR PROCESSING COMPLETE!")
    print(f"{'='*80}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSummary:")
    # print(f"  Total mentors: {len(mentors)}")
    print(f"  Successful mentors: {len(successful_mentors)}")
    print(f"  Mentors with issues: {len(failed_mentors)}")
    print(f"  Total questions processed: {total_processed}")
    print(f"  Total questions failed: {total_failed}")
    
    if successful_mentors:
        print(f"\nSuccessful mentors:")
        for mentor in successful_mentors:
            print(f"  [OK] {mentor}")
    
    if failed_mentors:
        print(f"\nMentors with issues:")
        for mentor in failed_mentors:
            print(f"  [FAILED] {mentor}")
    
    print(f"\nAll output files saved in: ./output/")


if __name__ == "__main__":
    # Run tests directly with pytest
    pytest.main([__file__, "-v", "--html=reports/report.html"])
