from ..settings import app, logger


async def get_channel_list():
    all_channels = []
    cursor = None

    while True:
        # Fetch a page of conversations asynchronously
        try:
            response = await app.client.conversations_list(
                limit=1000,                    # Recommended page size limit
                cursor=cursor,                # Pass the cursor for pagination
                types="public_channel",  # Specify channel types
                exclude_archived=False,
            )
        except Exception as e:  # noqa
            logger.error(f"Slack API error: {e}, retrying...")
            continue
        
        # Add the retrieved channels to your list
        all_channels.extend(response["channels"])
        
        # Check if there is a next page
        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
        logger.info(f"Fetching channel list... ({len(all_channels)})")

    return all_channels
