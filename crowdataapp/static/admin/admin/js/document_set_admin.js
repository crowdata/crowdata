window.$ = django.jQuery;
$(function(){
    $('td.field-field_type select').live('change', function() {

        $(this).parent()
            .siblings('.field-choices, .field-autocomplete, .field-placeholder_text')
            .children('input')
            .attr('disabled', 'disabled');

        switch(parseInt($(this).val())) {
            case 1:
            $(this).parent()
                .siblings('.field-autocomplete, .field-placeholder_text')
                .children('input')
                .removeAttr('disabled');
            break;
            case 4:
            case 5:
            case 6:
            case 7:
            case 8:
            $(this).parent()
                .siblings('.field-choices')
                .children('input')
                .removeAttr('disabled');

            this
            break;

        }
    });

    $('td.field-field_type select').trigger('change');


    // replace textareas with ACE
    $('textarea').each(function () {
        var textarea = $(this);

        switch(textarea.attr('name')) {
        case 'description':
        case 'form-0-intro':
            mode = 'text';
            break;
        case 'template_function':
            mode = 'javascript';
            break;
        case 'head_html':
            mode = 'html';
            break;
        }

        var editDiv = $('<div>', {
            position: 'absolute',
            width: textarea.width(),
            height: textarea.height(),
            'class': textarea.attr('class')
        }).css({
//            'top': textarea.offset()['top'],
            'left': textarea.offset()['left']
        }).insertBefore(textarea);

        textarea.css('visibility', 'hidden');

        var editor = ace.edit(editDiv[0]);
        editor.renderer.setShowGutter(true);
        editor.getSession().setValue(textarea.val());
        editor.getSession().setMode("ace/mode/" + mode);

        textarea.closest('form').submit(function () {
            textarea.val(editor.getSession().getValue());
        })

    });

});
