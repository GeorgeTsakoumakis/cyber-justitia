$(document).ready(function(){
    $('#flexRadioDefault1').change(function(){
        if($(this).is(':checked')) {
            $('#headlineFlair').empty();
        }
    });
    
    $('#flexRadioDefault2').change(function(){
        if($(this).is(':checked')) {
            $('#headlineFlair').append('<div class="input-group mb-3 style="padding-top: 4%"><input name="flair" type="text" id="headlineFlair" name="headlineFlair" placeholder="Describe your expertise in a short sentence" style="width: 500px;"></div>');
        }
    });
});