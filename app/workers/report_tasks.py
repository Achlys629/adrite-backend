from app.workers.celery_app import celery_app

@celery_app.task
def generate_invoice_report_task(client_id: int):
    # Will generate PDF invoice report
    # To be implemented with PDF library
    pass

@celery_app.task
def generate_analytics_report_task():
    # Will generate weekly analytics report
    pass