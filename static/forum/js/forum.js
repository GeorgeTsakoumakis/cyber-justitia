document.addEventListener("DOMContentLoaded", function() {
    // Function to adjust the font size based on the number of digits
    const upvoteElements = document.querySelectorAll('.upvote-count');

    upvoteElements.forEach(element => {
        adjustFontSize(element);
    });

    function adjustFontSize(element) {
        const textLength = element.textContent.length;
        if (textLength <= 2) {
            element.style.fontSize = '2rem';
        } else if (textLength === 3) {
            element.style.fontSize = '1.4rem';
        } else if (textLength === 4) {
            element.style.fontSize = '1.2rem';
        } else {
            element.style.fontSize = '1.0rem';
        }
    }
});

// Function to show when upvote/downvote button is pressed down
$(document).ready(function () {
    $('.vote-section').each(function () {
        var upvoteButton = $(this).find('.button_upvote');
        var downvoteButton = $(this).find('.button_downvote');

        upvoteButton.click(function () {
            $(this).toggleClass('active');
            if ($(this).hasClass('active')) {
                downvoteButton.removeClass('active');
            }
        });

        downvoteButton.click(function () {
            $(this).toggleClass('active');
            if ($(this).hasClass('active')) {
                upvoteButton.removeClass('active');
            }
        });
    });
});

// Function to add comment form
function addCommentForm() {
    const commentBox = document.getElementById('comment-box');
    // Make commentbox visible
    commentBox.style.display = 'block';
    const existingForm = commentBox.querySelector('.cloned-comment-form');
    if (existingForm === null) {
        let template = document.getElementById('comment-form-template');
        if (template) {
            let clone = template.cloneNode(true);
            clone.style.display = 'block';
            clone.removeAttribute('id');
            clone.classList.add('cloned-comment-form');

            let container = document.getElementById('comment-container');
            container.appendChild(clone);
        } else {
            // pass
        }
    }
}

// Function to remove comment form
function removeForm(button) {
    const form = button.closest('.cloned-comment-form');
    const mainBox = document.getElementById('comment-box');

    if (form) {
        form.remove();
    }

    if (mainBox) {
        mainBox.style.display = 'none';
    }
}

document.getElementById('submit-comment').onclick = function () {
    addCommentForm();
};
