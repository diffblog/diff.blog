"use strict";

import React, { useState, useEffect } from "react";

import {
  is_subscribed_to_topic,
  load_my_topics_left_sidebar_if_required,
} from "../topic";

import { show_login_prompt_if_required } from "./../helpers";

function followTopic(topicId, setIsFollowingTopic) {
  if (show_login_prompt_if_required("follow")) {
    return;
  }

  $.ajax({
    type: "POST",
    url: "/api/user/topics",
    data: { topic_ids: JSON.stringify([topicId]) },
    success: function (response) {
      load_my_topics_left_sidebar_if_required();
      setIsFollowingTopic(true);
    },
  });
}

function unFollowTopic(topicId, setIsFollowingTopic) {
  if (show_login_prompt_if_required("follow_topic")) {
    return;
  }

  $.ajax({
    type: "DELETE",
    url: "/api/user/topics",
    data: { topic_id: topicId },
    success: function (response) {
      load_my_topics_left_sidebar_if_required();
      setIsFollowingTopic(false);
    },
  });
}

function FollowingTopicButton({ topicId, setIsFollowingTopic }) {
  return (
    <button
      className="topic-following border py-1 px-2 rounded ml-auto text-white bg-gray-900 hover:bg-gray-800"
      onClick={() => unFollowTopic(topicId, setIsFollowingTopic)}
    >
      Following
    </button>
  );
}

function FollowTopicButton({ topicId, setIsFollowingTopic }) {
  return (
    <button
      className="topic-follow border py-1 px-2 rounded ml-auto border-gray-400 hover:border-gray-500"
      onClick={() => followTopic(topicId, setIsFollowingTopic)}
    >
      Follow
    </button>
  );
}

export function TopicFollowButton({ topicId }) {
  const [isFollowingTopic, setIsFollowingTopic] = useState(false);

  useEffect(() => {
    if (logged_in) {
      $.ajax({
        type: "GET",
        url: "/api/user/topics",
        success: function (my_topics) {
          const isFollowingTopicFromAPI = is_subscribed_to_topic(
            my_topics,
            topicId,
          );
          if (isFollowingTopic !== isFollowingTopicFromAPI) {
            setIsFollowingTopic(isFollowingTopicFromAPI);
          }
        },
      });
    }
  }, [isFollowingTopic]);

  if (isFollowingTopic) {
    return (
      <FollowingTopicButton
        topicId={topicId}
        setIsFollowingTopic={setIsFollowingTopic}
      />
    );
  }
  return (
    <FollowTopicButton
      topicId={topicId}
      setIsFollowingTopic={setIsFollowingTopic}
    />
  );
}
