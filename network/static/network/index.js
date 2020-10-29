//Bootstrap alert types for showing message
const success = "success"
const warning = "warning"
const danger = "danger"

document.addEventListener("DOMContentLoaded", function () {

  // Onsubmit method for adding post
  if (document.getElementById("add-post")) {
    document.getElementById("add-post").onsubmit = addPost
  }

  // Liking post
  if(document.querySelector(".like-btn")){
    document.querySelectorAll(".like-btn").forEach(function (el) {
      el.onclick = () => {
        likePost(el)
      }
    });
  }
  
  
  // Editing post
  if(document.querySelector(".edit-post")){
    document.querySelectorAll(".edit-post").forEach(function(btn) {
      btn.onclick = () => {
        editPost(btn)
      }
    })
  }

    // Follow post      
    if(document.getElementById("follow-btn")){
      document.getElementById("follow-btn").onclick = follow
      }
    
});

function addPost(e) {
  // Prevent post from doing default submission
  e.preventDefault();
  // Get the content value
  content = document.getElementById("post_content").value;

  // If content is not typed i.e blank do not let user to post
  if (content.length > 0) {
    // Post
    fetch(`/add_post`, {
      method: "POST",
      body: JSON.stringify(content),
    })
      .then((response) => response.json())
      .then((data) => {
        // If posted show message
        showMessage(data.message, success);
        // Reset value of post
        document.getElementById("post_content").value = "";
      });
  } else{
    // If textarea is empty show warning message
    showMessage("Type something to post", warning)
  }
};

function likePost(el){
    // Get data from the like button
    const user = el.dataset.likeuser;
    const post = el.dataset.likepost;

    // Check is user is logged in
    if (user !== "None") {
      // Toggle the classes to distinguish liked and unliked
      el.classList.toggle("fas");
      el.classList.toggle("far");

      // If user not liked put like 
      if (el.classList.contains("fas")) {
        fetch("/like_post", {
          method: "PUT",
          body: JSON.stringify({ post }),
        })
          .then((response) => response.json())
          .then((data) => {
            // Update count
            el.nextElementSibling.innerHTML = data.count;
          });
      }

      // If user liked put delete like 
      else if (el.classList.contains("far")) {
        fetch("/like_post", {
          method: "DELETE",
          body: JSON.stringify({ post }),
        })
          .then((response) => response.json())
          .then((data) => {
            // Update count
            el.nextElementSibling.innerHTML = data.count;
          });
      }
    }else{
        // If user is not logged in show a message to login
        showMessage("Login in to like the post", warning)
    }
}

function editPost(btn){
    // Get the postid using dataset set in the button
    const postId = btn.dataset.btnvalue
    // Getting the container of content itself
    const contentContainer = document.querySelector(`#content-${postId}`)
    
    //Check if the content in the card is textarea or paragraph
    if(contentContainer.firstChild.tagName === "TEXTAREA"){
      //Get edited value from textarea
      const newContent = document.querySelector(`#textarea-${postId}`).value
        // Send the data to backend using PUT method
        fetch(`/edit_post/${postId}`, {
          method: "PUT",
          body: JSON.stringify({
            content: newContent
          })
        })
        .then(response => response.json())
        .then(data => {
          if(data.error){
            showMessage(data.error, danger)
          }else{
            // Change the content with edited content
            contentContainer.innerHTML = data.content
            showMessage("Updated successfully", success)
            // Change back the button to edit
            btn.innerHTML = "Edit"
          }
        })

    }else{
      // Change btn name to save
      btn.innerHTML = "Save"
      //If the card doesn't have textarea element create one for editing
      const textArea = document.createElement("textarea")
      // Assign attributes to the textarea
      Object.assign(textArea, {
        name: "post_content",
        max_length: "255",
        rows: "3",
        className: "form-control",
        id: `textarea-${postId}`,
        // Prefill with previousContent
        value: `${contentContainer.innerHTML}`,
      })
      // Replace the previouscontent with textarea
      contentContainer.firstChild.replaceWith(textArea)
    }
  }

  //follw post function takes event as parameter
  function follow(e){
    // get the button from event
    const btn = e.target
    // Get also the user to follow from the dataset
    const userIdToFollow = btn.dataset.user

    // If user if already following so this function
    if(btn.dataset.following === "true"){
      // Send a delete request to follow route 
      // along with userId of whom current user have to unfollow
      fetch(`/follow`, {
        method: "DELETE",
        body: JSON.stringify({user: userIdToFollow})
      })
      .then(response => response.json())
      .then(data => {
        // When data received decrease the count
        document.querySelector("#followers-count").innerHTML = data.followers_count
        // Change the dataset value of following to false meaning current user is no longer following
        btn.dataset.following = !Boolean(btn.dataset.following)
        // Change the button to a follow btn
        document.querySelector("#follow-btn").innerText = "Follow"
      })
    }else{ // If user is not following do this
      // Do a fetch request as same as did for unfollow but with POST request along with user id of user to follow
      fetch(`/follow`, {
        method: "POST",
        body: JSON.stringify({user: userIdToFollow})
      })
      .then(response => response.json())
      .then(data => {
        // If user tries to follow themselves show error message that cannot be done
        if(data.error){
          showMessage(data.error, warning)
        }else{
          // Increase the count
          document.querySelector("#followers-count").innerHTML = data.followers_count
          // Change the dataset value to true to indicate the current user started following
          btn.dataset.following = !Boolean(btn.dataset.following)
          // Change the button to an unfollow btn so current user can unfollow
          document.querySelector("#follow-btn").innerText = "Unfollow"
        }
      })
    }
  }

// Show a fixed alert message at the top of the page
function showMessage(message, type) {
  // Get a div section that is created for message
  const messageElement = document.getElementById("message");
  // Change style to block to display
  messageElement.style.display = "block";
  // Set the innerHTML to the message
  messageElement.innerHTML = message;
  // Add class typetag
  messageElement.classList.add(`alert-${type}`);
  //Display none after few seconds
  setTimeout(() => {
    messageElement.innerHTML = "";
    messageElement.style.display = "none";
    messageElement.classList.remove(`alert-${type}`);
  }, 3000);
}
