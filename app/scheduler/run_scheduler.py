from apscheduler.schedulers.blocking import BlockingScheduler
from app.planner.research_agent import run_research_pipeline

scheduler = BlockingScheduler(timezone="America/Sao_Paulo")


@scheduler.scheduled_job("cron", day_of_week="sun", hour=8, minute=0)
def weekly_research_job():
    print("Rodando pipeline semanal de pesquisa...")
    run_research_pipeline()


if __name__ == "__main__":
    print("Scheduler iniciado - pipeline roda toda domingo às 08:00 (America/Sao_Paulo).")
    print("Deixe este processo rodando continuamente (Ctrl+C para parar).")
    scheduler.start()