// Util functions
const displayMessage = (content, role = "user", isOngoing = false) => {
  const messageHTML = createMessageHTML(content, role);
  $("#chat-messages").append(messageHTML);
  if (isOngoing) {
    $(`.bg-green-100:last`).parent().addClass("ai-processing");
  }
};

const createMessageHTML = (content, role) => {
  const messageClasses = role === "user" ? "bg-blue-200 text-black" : "bg-green-100 text-black";
  const messageRole = role === "user" ? "user" : "assistant";
  const beforeContent = role === "user" ? 'before:bg-blue-500' : 'before:bg-gray-300';

  return `<div class="flex justify-${role === "user" ? "end" : "start"} mb-2">
            <div class="rounded-lg p-3 max-w-lg lg:max-w-xl relative ${messageClasses} before:absolute before:inset-r-0 before:w-3 before:h-3 before:${beforeContent} before:transform before:-rotate-45 before:-translate-y-1/2">
              ${content}
            </div>
          </div>`;
};

const scrollToBottom = () => {
  setTimeout(() => {
    const chatBox = document.getElementById("chat-messages");
    chatBox.scrollTop = chatBox.scrollHeight;
  }, 100);
};

// Message sending function
const sendMessage = () => {
  const userMessage = $("#user-input").val().trim();

  if (!userMessage) {
    alert("Message cannot be empty!");
    return;
  }

  displayMessage(userMessage, "user", true);
  scrollToBottom();

  $("#user-input").val("");
  toggleSendButton();

  $.ajax({
    type: "POST",
    url: "/determine-response",
    data: JSON.stringify({ user_message: userMessage }),
    contentType: "application/json",
    dataType: "json",
    success: handleResponseSuccess,
    error: handleResponseError,
  });
};

// Response handling functions
const handleResponseSuccess = (data) => {
  $(".ai-processing").remove();
  displayMessage(data.message, "assistant");
  scrollToBottom();

  if (data.objective) {
    displayTaskWithStatus(`Task: ${data.objective}`, "ongoing", data.skill_used, data.task_id);
  }

  if (data.path !== "ChatCompletion") {
    checkTaskCompletion(data.task_id);
  }
};

const handleResponseError = (error) => {
  $(".ai-processing").remove();
  const errorMessage =
    error.responseJSON && error.responseJSON.error
      ? error.responseJSON.error
      : "Unknown error";
  displayMessage(`Error: ${errorMessage}`, "error");
  scrollToBottom();
};

// Task management functions
const toggleSendButton = () => {
  $("#user-input").val().trim()
    ? $("button").prop("disabled", false)
    : $("button").prop("disabled", true);
};

const checkTaskCompletion = (taskId) => {
  $.ajax({
    type: "GET",
    url: `/check-task-status/${taskId}`,
    dataType: "json",
    success(data) {
      if (data.status === "completed") {
        updateTaskStatus(taskId, "completed", data.output);
        fetchTaskOutput(taskId);
        displayMessage("Hey, I just finished a task!", "assistant");
      } else {
        fetchTaskOutput(taskId);
        setTimeout(() => {
          checkTaskCompletion(taskId);
        }, 5000);
      }
    },
    error(error) {
      console.error(`Error checking task status for ${taskId}:`, error);
    },
  });
};

const fetchTaskOutput = (taskId) => {
  $.ajax({
    type: "GET",
    url: `/fetch-task-output/${taskId}`,
    dataType: "json",
    success(data) {
      if (data.output) {
        const $taskItem = $(`.task-item[data-task-id="${taskId}"]`);
        const $outputContainer = $taskItem.find(".task-output p");

        $outputContainer.html(data.output);
      }
    },
    error(error) {
      console.error(`Error fetching task output for ${taskId}:`, error);
    },
  });
};

// Initialization and event handling
$(document).ready(function () {
  toggleSendButton();
  loadPreviousMessages();
  loadAllTasks();

  $("#send-btn").on("click", sendMessage);
  $("#user-input").on("input", toggleSendButton);
  $("#user-input").on("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  $("#task-search").on("keyup", function () {
    const value = $(this).val().toLowerCase();
    $(".task-item").filter(function () {
      $(this).toggle(
        $(this).find(".task-title").text().toLowerCase().indexOf(value) > -1
      );
    });
  });
});

// Previous messages loading function
const loadPreviousMessages = () => {
  $.ajax({
    type: "GET",
    url: "/get-all-messages",
    dataType: "json",
    success(data) {
      data.forEach((message) =>
        displayMessage(message.content, message.role, message.isOngoing)
      );
      scrollToBottom();
    },
    error(error) {
      console.error("Error fetching previous messages:", error);
    },
  });
};


