def click(page, step, logger):
    selector = step["selector"]

    logger.info(f"Click {selector}")
    page.click(selector)
