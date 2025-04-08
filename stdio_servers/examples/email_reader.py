"""
FastMCP Email Reader Example
"""
from mcp.server.fastmcp import FastMCP
import logging

#Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

#Create server
mcp = FastMCP("Email Reader")


@mcp.tool()
def get_emails(email_provider: str, email_status: str ="all") -> str:
    """Get emails from an email service provider

    Args:
        email_provider: The email service provider like hotmail or yahoo , gmail etc
        email_status: Type of emails to retrieve, it musb be one of ['read', 'unread', 'all']"
    """
    #Retrieve emails ...
    
    # Gmail: Read emails
    gmail_read_emails = (
        "from: emily.watson@gmail.com\n"
        "full name: Emily Watson\n"
        "title: Vacation Request\n"
        "body: Hi Manager, I’d like to request vacation days from June 10 to June 15.\n"
        "status: read\n"
    )

    # Gmail: Unread emails
    gmail_unread_emails = (
        "from: john.doe@gmail.com\n"
        "full name: John Doe\n"
        "title: Weekly Report\n"
        "body: Please find attached the weekly report for our project status update.\n"
        "status: unread\n"
    )

    # Yahoo: Read emails
    yahoo_read_emails = (
        "from: linda.green@yahoo.com\n"
        "full name: Linda Green\n"
        "title: Travel Itinerary\n"
        "body: Here’s the travel itinerary for our upcoming conference in Chicago.\n"
        "status: read\n"
    )

    # Yahoo: Unread emails
    yahoo_unread_emails = (
        "from: michael_ross@yahoo.com\n"
        "full name: Michael Ross\n"
        "title: Feedback on Report\n"
        "body: The report looks good overall. I have a few suggestions attached below.\n"
        "status: unread\n"
    )

    # Hotmail: Read emails
    hotmail_read_emails = (
        "from: sarah.connor@hotmail.com\n"
        "full name: Sarah Connor\n"
        "title: Account Security Alert\n"
        "body: We noticed a new login to your account from a different location. Please review your recent activity.\n"
        "status: read\n"
    )

    # Hotmail: Unread emails
    hotmail_unread_emails = (
        "from: mark.brown@hotmail.com\n"
        "full name: Mark Brown\n"
        "title: Job Opportunity\n"
        "body: I came across your profile and wanted to discuss a potential job opportunity with you.\n"
        "status: unread\n"
    )

    #keywords
    gmail="gmail"
    hotmail="hotmail"
    yahoo="yahoo"
    read="read"
    unread="unread"
    all="all"

    #return the requested emails type
    if email_provider ==gmail and email_status==read:
        return gmail_read_emails
    elif email_provider ==gmail and email_status==unread:
        return gmail_unread_emails
    elif email_provider ==gmail and email_status==all:
        return gmail_read_emails+"\n"+gmail_unread_emails
    elif email_provider ==hotmail and email_status==read:
        return hotmail_read_emails
    elif email_provider ==hotmail and email_status==unread:
        return hotmail_unread_emails
    elif email_provider ==hotmail and email_status==all:
        hotmail_read_emails+"\n"+hotmail_unread_emails
    elif email_provider ==yahoo and email_status==read:
        return yahoo_read_emails
    elif email_provider ==yahoo and email_status==unread:
        return yahoo_unread_emails
    elif email_provider ==yahoo and email_status==all:
        return yahoo_read_emails+"\n"+yahoo_unread_emails
    
    email_status_list = [read, unread, all]
    if email_status not in email_status_list:
        return f"{email_status} is not a valid email type, the email_status must be in {email_status_list}"
    return f"Unknown Email Service Provider: {email_provider}."


if __name__ == "__main__":
    mcp.run(transport="stdio")