document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  document.querySelector("#compose-form").onsubmit = (e) => {
    e.preventDefault();
    const recipients = document.querySelector("#compose-recipients").value;
    const subject = document.querySelector("#compose-subject").value;
    const body = document.querySelector("#compose-body").value;

    const mail = {
      recipients,
      subject,
      body,
    };

    fetch(`/emails`, {
      method: "POST",
      body: JSON.stringify(mail),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data.error) {
          throwMessage(data.error, "alert-danger");
        } else {
          throwMessage(data.message, "alert-primary");

          load_mailbox("sent");
        }
      });
  };
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((data) => {
      data.map((data) => {
        //Show all mail
        showMail(data.id, data.sender, data.subject, data.timestamp, data.read);

        //Onclick take the user to the mail page
        document.querySelectorAll(".mail-list").forEach(function (el) {
          el.onclick = function () {
            fetch(`/emails/${this.dataset.id}`, {
              method: "PUT",
              body: JSON.stringify({
                read: true,
              }),
            });

            fetch(`/emails/${this.dataset.id}`)
              .then((response) => response.json())
              .then((data) => {
                document.querySelector("#emails-view").style.display = "block";
                document.querySelector("#compose-view").style.display = "none";

                document.querySelector("#emails-view").innerHTML = viewMail(
                  data.id,
                  data.sender,
                  data.recipients,
                  data.subject,
                  data.timestamp,
                  data.body,
                  data.archived
                );

                //Reply button
                if (document.querySelector(".reply")) {
                  document.querySelector(".reply").onclick = function () {
                    compose_email();
                    document.querySelector("#compose-recipients").value =
                      data.sender;
                    document.querySelector(
                      "#compose-subject"
                    ).value = data.subject.includes("Re:")
                      ? data.subject
                      : `Re: ${data.subject}`;
                    document.querySelector(
                      "#compose-body"
                    ).value = `On ${data.timestamp} ${data.sender} wrote: ${data.body}`;
                  };
                }

                //archive button
                if (document.querySelector(".archive")) {
                  document.querySelector(".archive").onclick = function () {
                    const setArchived = this.dataset.setarchived === "true";
                    console.log(setArchived);
                    fetch(`emails/${this.dataset.id}`, {
                      method: "PUT",
                      body: JSON.stringify({
                        archived: setArchived,
                      }),
                    });
                    load_mailbox("inbox");
                  };
                }
              });
          };
        });
      });
    })
    .catch((err) => console.log(err));
}

//Show message when data arrives
function throwMessage(message, alertClass) {
  const messageElement = document.getElementById("message");
  messageElement.style.display = "block";
  messageElement.innerHTML = message;
  messageElement.classList.add(alertClass);
  setTimeout(() => {
    messageElement.style.display = "none";
  }, 5000);
}

//show mailbox list
function showMail(id, sender, subject, receivedTime, read) {
  const emailsView = document.getElementById("emails-view");

  const mailList = document.createElement("div");
  mailList.classList.add("mail-list");

  const mailDescription = document.createElement("div");
  mailDescription.classList.add("mail-list-description");
  const senderP = document.createElement("p");
  senderP.innerHTML = sender;
  mailDescription.append(senderP);
  const subjectP = document.createElement("p");
  subjectP.innerHTML = subject;
  subjectP.style.color = "#5f6368";
  mailDescription.append(subjectP);
  mailList.append(mailDescription);

  const rightDiv = document.createElement("div");
  rightDiv.classList.add("mail-list-description");
  timeP = document.createElement("p");
  timeP.innerHTML = receivedTime;
  rightDiv.append(timeP);
  rightDiv.style.color = "#5f6368";
  mailList.append(rightDiv);
  mailList.dataset.id = id;
  mailList.style.backgroundColor = read ? "#e4e8ed" : "";

  emailsView.append(mailList);
}

//View the actual mail
function viewMail(id, from, to, subject, timestamp, body, archived) {
  const sentMail = document.getElementById("my-mail").innerHTML === from;
  const replyButton = `
  <button class="btn btn-sm btn-outline-primary reply">Reply</button>
  `;
  const archiveButton = `
  <button data-id="${id}" data-setarchived=${
    archived ? false : true
  } class="btn btn-sm btn-outline-primary archive">${
    archived ? "Unarchive" : "Archive"
  }</button>
  `;

  return `<div>
        <p><b>From:</b> ${from}</p>
        <p><b>To:</b> ${to}</p>
        <p><b>Subject:</b> ${subject}</p>
        <p><b>Time</b>: ${timestamp}</p>
        ${sentMail || archived ? "" : replyButton}
        ${sentMail ? "" : archiveButton}
        <hr>
        <p>${body}</p>
       </div>
      `;
}
