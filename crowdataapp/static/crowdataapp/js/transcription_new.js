// https://github.com/spencertipping/jquery.fix.clone
(function (original) {
  jQuery.fn.clone = function () {
    var result           = original.apply(this, arguments),
        my_textareas     = this.find('textarea').add(this.filter('textarea')),
        result_textareas = result.find('textarea').add(result.filter('textarea')),
        my_selects       = this.find('select').add(this.filter('select')),
        result_selects   = result.find('select').add(result.filter('select'));

    for (var i = 0, l = my_textareas.length; i < l; ++i) $(result_textareas[i]).val($(my_textareas[i]).val());
    for (var i = 0, l = my_selects.length;   i < l; ++i) result_selects[i].selectedIndex = my_selects[i].selectedIndex;

    return result;
  };
}) (jQuery.fn.clone);

$(function() {
  $('form[method="post"]')[0].reset();
  var FORM_SUBMITTED = gettext('<h1>Thanks for your help!</h1><button id="another">Want another file?</button>');

  var input_mask_options = {
    radixPoint: ',',
    groupSeparator: '.',
    autoGroup: true,
    autoUnmask: true
  };

  $('form').on('submit', function(event) {
    event.preventDefault();
    var form_copy = $(this).clone();
    //console.log(form_copy);
    // $('input[data-number=true]', form_copy).each(function() { // bug in replace comma
    //   $(this).val($(this).val()
    //               .replace(input_mask_options.radixPoint, '.')
    //               .replace(input_mask_options.groupSeparator, ''));
    //   console.log($(this).val())
    // });
    $('input[data-number=true]', form_copy).val(function(){ return this.value.replace(",", ".")});
    var serializedForm = $(form_copy).serialize();
    // console.log(serializedForm);

    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      headers: {
        'X-CSRFToken': $.cookie('csrftoken')
      },
      data: serializedForm,
      success: function(data) {
        // $('#form-container').html(FORM_SUBMITTED);

        var social = new create_sosial($('.herramientasSociales.social'), doc_url, 'Revisé #GastosdelSenado en #Vozdata. ¡Sumate!');
        $('#form-container').html("");
        $("#social_document").show();
        $("html, body").animate({ scrollTop:0 }, 800);
      },
      error: function(data, s, m) {
        alert('Ocurrió un error.\nVerifique su conexión a internet e intente mas tarde');
        console.log(data);
      }
    });
  });

  $(document).on('click',
                 '#another',
                 function(data) {
                   var parts = location.pathname.split('\/');
                   location = '/' + parts[1] + '/' + parts[2] + '/new_transcription';
                 });

  $('input[type=text][data-verify=True]').each(function() {
    var $el = $(this);
    var $spinner = $("img.spinner", $el.closest('.vd_label'));

    $el.typeahead({
      name: $(this).attr('name'),
      minLength: 3,
      remote: {
        url: 'autocomplete/' + $(this).attr('name') + '?q=%QUERY',
        beforeSend: function(xhr){
          $spinner.show();
        },
        filter: function(parsedResponse){
            $spinner.hide();
            return parsedResponse;
        }
      }
    });
  });

  $('input[type=number]').keydown(function(e){ // only numbers
    var key = e.charCode || e.keyCode || 0;
    return ( key == 8 || key == 46 || key == 188 || (key >= 35 && key <= 40) || (key >= 48 && key <= 57) || (key >= 96 && key <= 105)); 
  })
  .attr('type', 'text')
  .attr('data-number', 'true')
  .css("text-align", "right");

/* bug in replace comma
  $('input[type=number]').each(function() {
    var input = $(this);
    input
      .attr('type', 'text')
      .attr('data-number', 'true')
      .inputmask('decimal', input_mask_options);
  });
*/
  $('div.label_bco_enviar a').click(function(e) {
    e.preventDefault();
    window.location.reload();
  });

  /* datepicker */
  /*
  var date = $("[type='date']").datepicker({
    format: "dd/mm/yyyy"
    })
     .on('changeDate', function(ev) {
       date.datepicker('hide');
     });
  */

  /* help butons */
  var popup = new Popup();
  var tmpl_slide = $("#templateslide").html();
  $(".ayuda img").click(function(){
    popup.show_p({title: "Ayuda", body:tmpl_slide}, function(){
     var config= { // configuracion slide
        "ul" : $("ul#list"),
        "next":$("a.next"),
        "prev":$("a.prev"),
        "efecto_animacion":null
      }
      var slide= simple_slide(config); //start slide
    });
  })

});
