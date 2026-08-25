import logging

logger = logging.getLogger("saans.distribution_wiring")


def register_distribution_hooks() -> None:
    from app.jobs.scoring_cycle import register_post_scoring_hook

    try:
        from distribution.pdf.generate_bulletin import on_scores_computed as generate_pdf_hook

        register_post_scoring_hook(generate_pdf_hook)
    except ImportError:
        logger.warning("PDF bulletin module not available, skipping that hook")

    try:
        from distribution.whatsapp.bot import on_scores_computed as broadcast_whatsapp_hook

        register_post_scoring_hook(broadcast_whatsapp_hook)
    except ImportError:
        logger.warning("WhatsApp bot module not available, skipping that hook")
