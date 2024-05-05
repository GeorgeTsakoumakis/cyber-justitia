document.addEventListener("DOMContentLoaded", function() {
    var radioButtons = document.querySelectorAll('input[type="radio"][name="user_type"]');
    var flairInput = document.getElementById('flair');

    // Function to show/hid flair input based on radio button selection
    function toggleFlairInput() {
        if (this.value === 'professional') {
            flairInput.style.display = 'block';
        } else {
            flairInput.style.display = 'none';
        }
    }

    // Attach change event listener to radio buttons
    radioButtons.forEach(function(radioButton) {
        radioButton.addEventListener('change', toggleFlairInput);
    });

    // Trigger initial state
    toggleFlairInput.call(document.querySelector('input[type="radio"][name="user_type"]:checked'));
});document.addEventListener("DOMContentLoaded", function() {
    var radioButtons = document.querySelectorAll('input[type="radio"][name="user_type"]');
    var flairInput = document.getElementById('flair');

    // Function to show/hide flair input based on radio button selection
    function toggleFlairInput() {
        if (this.value === 'professional') {
            flairInput.style.display = 'block';
        } else {
            flairInput.style.display = 'none';
        }
    }

    // Attach change event listener to radio buttons
    radioButtons.forEach(function(radioButton) {
        radioButton.addEventListener('change', toggleFlairInput);
    });

    // Trigger initial state
    toggleFlairInput.call(document.querySelector('input[type="radio"][name="user_type"]:checked'));
});