import { TopicFollowButton } from "./../components/TopicFollowButton";
import React from "react";
import ReactDOM from "react-dom/client";

$(function () {
  const like_button_holder = document.querySelector(
    "#topic-follow-button-holder",
  );
  const topicId = like_button_holder.getAttribute("data-topic-id");
  const root = ReactDOM.createRoot(like_button_holder);
  root.render(<TopicFollowButton topicId={topicId} />);
});
