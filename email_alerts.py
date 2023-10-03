"""
Send an email with Python.email

Author: Denise Case
Date: 2022-12-27

Modified by: Beth Harvey
Date: 2023-09-25

We'll need an outgoing email service -
this example uses a gmail account.

uses:

 - smtplib - for transmission via smtp
 - email - handy EmailMessage class
 - tomllib - to read TOML files
 - try / except / finally to handle errors
 - .env.toml - to keep secrets (requires Python 3.11)
 - typehints - to help with code understanding

--------------------------------

Sending with your Gmail Account

Step 1: Check that IMAP is turned on
 - On your computer, open Gmail.
 - In the top right, click Settings Settings and then See all settings.
 - Click the 'Forwarding and POP/IMAP' tab.
 - In the "IMAP access" section, select 'Enable IMAP'.
-  Click Save Changes.

GMAIL Outgoing - settings for the client

smtp.gmail.com
Requires SSL: Yes
Requires TLS: Yes (if available)
Requires Authentication: Yes
Port for TLS/STARTTLS: 587

Enable Two factor authentication: 
- https://support.google.com/accounts/answer/185833?hl=en
- Account / security / app passwords / 
- select app / select device / generate 
- I generated an app password for my Mac
- paste the 16-char as your password


"""

import smtplib
from email.message import EmailMessage
import tomllib  # requires Python 3.11
import pprint

# define functions here


def createAndSendEmailAlert(email_subject: str, email_body: str):

    """Read outgoing email info from a TOML config file"""

    with open(".env.toml", "rb") as file_object:
        secret_dict = tomllib.load(file_object)
    # pprint.pprint(secret_dict)

    # basic information

    host = secret_dict["outgoing_email_host"]
    port = secret_dict["outgoing_email_port"]
    outemail = secret_dict["outgoing_email_address"]
    outpwd = secret_dict["outgoing_email_password"]

    # Create an instance of an EmailMessage

    msg = EmailMessage()
    msg["From"] = secret_dict["outgoing_email_address"]
    msg["To"] = secret_dict["outgoing_email_address"]
    msg["Reply-to"] = secret_dict["outgoing_email_address"]
    # email_subject = "Email from Data Analyst and Python Developer"
    # email_body = "Did you know the Python stadard library enables emailing?"

    msg["Subject"] = email_subject
    msg.set_content(email_body)

    print("========================================")
    print(f"Prepared Email Message: ")
    print("========================================")
    print()
    print(f"{str(msg)}")
    print("========================================")
    print()

    # Communications can fail, so use:

    # try -   to execute the code
    # except - when you get an Exception, do something else
    # finally - clean up regardless

    # Create an instance of an email server, enable debug messages

    server = smtplib.SMTP(host)
    server.set_debuglevel(2)

    print("========================================")
    print(f"SMTP server created: {str(server)}")
    print("========================================")
    print()

    try:
        print()
        server.connect(host, port)  # 465
        print("========================================")
        print(f"Connected: {host, port}")
        print("So far so good - will attempt to start TLS")
        print("========================================")
        print()

        server.starttls()
        print("========================================")
        print(f"TLS started. Will attempt to login.")
        print("========================================")
        print()

        try:
            server.login(outemail, outpwd)
            print("========================================")
            print(f"Successfully logged in as {outemail}.")
            print("========================================")
            print()

        except smtplib.SMTPHeloError:
            print("The server did not reply properly to the HELO greeting.")
            exit()
        except smtplib.SMTPAuthenticationError:
            print("The server did not accept the username/password combination.")
            exit()
        except smtplib.SMTPNotSupportedError:
            print("The AUTH command is not supported by the server.")
            exit()
        except smtplib.SMTPException:
            print("No suitable authentication method was found.")
            exit()
        except Exception as e:
            print(f"Login error. {str(e)}")
            exit()

        try:
            server.send_message(msg)
            print("========================================")
            print(f"Message sent.")
            print("========================================")
            print()
        except Exception as e:
            print()
            print(f"ERROR: {str(e)}")
        finally:
            server.quit()
            print("========================================")
            print(f"Session terminated.")
            print("========================================")
            print()

    # Except if we get an Exception (we call e)

    except ConnectionRefusedError as e:
        print(f"Error connecting. {str(e)}")
        print()

    except smtplib.SMTPConnectError as e:
        print(f"SMTP connect error. {str(e)}")
        print()


if __name__ == "__main__":
    subject_str = ("Email from Data Analyst and Python Developer",)
    content_str = ("Did you know the Python stadard library enables emailing?",)

    email_message = createAndSendEmailAlert(
        email_subject=subject_str, email_body=content_str
    )