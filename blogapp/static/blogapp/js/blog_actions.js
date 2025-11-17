// JS to handle like, add comment, delete comment via AJAX (fetch API)

function getCSRFToken() {
  const cookieValue = document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="));
  return cookieValue ? cookieValue.split("=")[1] : "";
}

// Helper to make POST request with CSRF
async function postJSON(url, formData) {
  // include CSRF token header so Django accepts AJAX POSTs when using session auth
  const headers = {
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRFToken": getCSRFToken(),
  };
  // If formData is a FormData instance, let fetch handle content-type
  const opts = {
    method: "POST",
    headers: headers,
    credentials: "same-origin",
    body: formData,
  };
  return fetch(url, opts)
    .then((res) => res.json().then((data) => ({ status: res.status, data })))
    .catch((err) => ({ status: 500, data: { error: err.message } }));
}

// Like/unlike handler
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss bootstrap alerts after a short delay (default 4s)
  function autoDismissAlerts(timeout = 4000) {
    document.querySelectorAll(".alert").forEach((alert) => {
      // allow opt-out by adding `data-autodismiss="false"` to the alert
      if (alert.dataset.autodismiss === "false") return;
      // Only dismiss visible alerts
      setTimeout(() => {
        try {
          // If Bootstrap's JS is present, prefer its close() to trigger proper events
          if (window.bootstrap && bootstrap.Alert) {
            const a = bootstrap.Alert.getOrCreateInstance(alert);
            a.close();
            return;
          }
        } catch (e) {
          // fall back to manual removal
        }
        // Fade out then remove (smooth fallback if Bootstrap JS not loaded)
        alert.classList.remove("show");
        alert.style.transition =
          alert.style.transition ||
          "opacity .35s linear, height .35s linear, margin .35s linear, padding .35s linear";
        alert.style.opacity = "0";
        alert.style.paddingTop = "0";
        alert.style.paddingBottom = "0";
        alert.style.marginTop = "0";
        alert.style.marginBottom = "0";
        // remove after transition
        setTimeout(() => {
          if (alert.parentNode) alert.parentNode.removeChild(alert);
        }, 400);
      }, timeout);
    });
  }

  // run auto-dismiss on DOM ready
  autoDismissAlerts(4000);

  // Like form
  document.querySelectorAll(".like-form").forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const url = form.getAttribute("action");
      const formData = new FormData(form);
      // fetch
      const res = await postJSON(url, formData);
      if (res.status === 200) {
        const liked = res.data.liked;
        const count = res.data.like_count;
        const btn = form.querySelector(".like-button");
        btn.textContent = liked ? "Unlike" : "Like";
        const countSpan = document.getElementById("like-count");
        if (countSpan) countSpan.textContent = count;
      } else if (res.data && res.data.error) {
        alert(res.data.error);
      }
    });
  });

  // Comment form
  document.querySelectorAll(".comment-form").forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const url = form.getAttribute("action");
      const formData = new FormData(form);
      const res = await postJSON(url, formData);
      if (res.status === 200) {
        const data = res.data;
        // remove 'No comments yet' placeholder if present
        const noComments = document.getElementById("no-comments");
        if (noComments) noComments.remove();
        // create comment HTML
        const commentsList = document.getElementById("comments-list");
        const div = document.createElement("div");
        div.className = "border rounded p-2 mb-2 comment-item";
        div.id = "comment-" + data.id;
        div.setAttribute("data-comment-id", data.id);
        div.innerHTML = `\n          <div class="d-flex justify-content-between">\n            <strong>${data.user}</strong>\n            <small class="text-muted">${data.created_at}</small>\n          </div>\n          <div class="comment-content">${data.content}</div>\n        `;
        // add delete button if current user is owner or blog author
        const currentUser = commentsList.dataset.currentUser || "";
        const blogAuthor = commentsList.dataset.blogAuthor || "";
        if (data.user === currentUser || blogAuthor === currentUser) {
          const delForm = document.createElement("form");
          delForm.method = "post";
          delForm.action = `/comment/${data.id}/delete/`;
          delForm.className = "mt-1 delete-comment-form";
          delForm.setAttribute("data-comment-id", data.id);
          // CSRF token input
          const csrfInput = document.createElement("input");
          csrfInput.type = "hidden";
          csrfInput.name = "csrfmiddlewaretoken";
          csrfInput.value = getCSRFToken();
          delForm.appendChild(csrfInput);
          const btn = document.createElement("button");
          btn.type = "submit";
          btn.className = "btn btn-sm btn-outline-danger";
          btn.textContent = "Delete";
          delForm.appendChild(btn);
          div.appendChild(delForm);
        }
        commentsList.prepend(div);
        // clear input
        form.querySelector('input[name="content"]').value = "";
        // attach delete handler if delete form exists inside (unlikely here)
      } else if (res.data && res.data.error) {
        alert(res.data.error);
      }
    });
  });

  // Delete comment forms
  document.addEventListener("click", async function (e) {
    const el = e.target;
    if (
      el.matches(".delete-comment-form button") ||
      el.closest(".delete-comment-form button")
    ) {
      e.preventDefault();
      const btn = el.closest("button") || el;
      const form = btn.closest(".delete-comment-form");
      if (!form) return;
      if (!confirm("Delete this comment?")) return;
      const url = form.getAttribute("action");
      const formData = new FormData(form);
      const res = await postJSON(url, formData);
      if (res.status === 200 && res.data.deleted) {
        const cid = res.data.comment_id;
        const node = document.getElementById("comment-" + cid);
        if (node) node.remove();
      } else if (res.data && res.data.error) {
        alert(res.data.error);
      }
    }
  });
});
