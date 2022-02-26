import {
    setup_ajax,
    show_login_prompt_if_required,
    send_event,
} from "./helpers";
  setup_ajax();
  var topic_item_sidebar_template = require("./../templates/topic-item-home-sidebar.handlebars");
  var topic_follow_template = require("./../templates/topic-follow-button.handlebars")

  function is_subscribed_to_topic(my_topics, topic_id) {
      for (let my_topic of my_topics) {
          if (my_topic.id === parseInt(topic_id)) {
              return true;
          }
      }
      return false;
  }

  function load_my_topics_sidebar() {
    $.ajax({
      type: "GET",
      url: "/api/user/topics",
      success: function (my_topics) {
          $("#my-topics").empty()
          for (let topic of my_topics) {
              const html = topic_item_sidebar_template(topic);
              $("#my-topics").append(html);
          }

          if($("#topic-follow-button-holder").length) {
              const page_topic_id = $("#topic-follow-button-holder").data("topic-id");
              let html;
              if(is_subscribed_to_topic(my_topics, page_topic_id)) {
                  html = topic_follow_template({following: true, id: page_topic_id})
              } else {
                  html = topic_follow_template({following: false, id: page_topic_id})
              }
              $("#topic-follow-button-holder").html(html);
          }
      }
  });
  }

  $(function () {
    if($("#my-topics").length) {
       load_my_topics_sidebar();
    }

    if($("#popular-topics").length) {
      $.ajax({
          type: "GET",
          url: "/api/topics/popular",
          success: function (popular_topics) {
              for (let topic of popular_topics) {
                  const html = topic_item_sidebar_template(topic);
                  $("#popular-topics").append(html);
              }
              
              if($("#topic-follow-button-holder").length) {
                  const page_topic_id = $("#topic-follow-button-holder").data("topic-id");
                  const html = topic_follow_template({following: false, id: page_topic_id})
                  $("#topic-follow-button-holder").html(html);
              }
          }
      });
    }
      
      $(function () {
        $("body").on("click", ".topic-following", function () {
          if (show_login_prompt_if_required("follow_topic")) {
            return;
          }
          send_event("unfollow_topic");
          const topic_id = $(this).data("topic-id");
          
          $.ajax({
            type: "DELETE",
            url: "/api/user/topics",
            data: { topic_id:  topic_id},
            success: function (response) {
              load_my_topics_sidebar();
            },
            });

        });

        $("body").on("click", ".topic-follow", function () {
          if (show_login_prompt_if_required("follow")) {
            return;
          }
          send_event("follow_topic");
          const topic_id = $(this).data("topic-id");
      
      
          $.ajax({
            type: "POST",
            url: "/api/user/topics",
            data: { topic_ids: JSON.stringify([topic_id])},
            success: function (response) {
              load_my_topics_sidebar();
            },
          });
        });

      });
      


  });
  