$(function() {
  $("#childNode").detach().appendTo("#parentNode");
  $('#documentsetformentry_set-group table td input[type=hidden]').detach().appendTo('form');
  $('#documentsetformentry_set-group table th:first-child, #documentsetformentry_set-group table td:first-child, #documentsetformentry_set-group table td:nth-child(2)').remove();
});
