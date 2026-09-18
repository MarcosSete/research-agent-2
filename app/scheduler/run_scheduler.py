from apscheduler.schedulers.blocking import BlockingScheduler

from app.planner.research_agent import run_research_pipeline


scheduler = BlockingScheduler(timezone="America/Sao_Paulo")


@scheduler.scheduled_job("cron", day_of_week="sun", hour=8, minute=0)
def weekly_research_job():
    print("Running weekly research pipeline...")
    run_research_pipeline()


if __name__ == "__main__":
    print("Scheduler started - pipeline runs every Sunday at 08:00 (America/Sao_Paulo).")
    print("Keep this process running continuously (Ctrl+C to stop).")
    scheduler.start()
