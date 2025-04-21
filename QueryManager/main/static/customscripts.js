//Prevent pagination from refreshing the filter
document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('question-container');

    container.addEventListener('click', function (e) {
      if (e.target.tagName === 'A' && e.target.closest('.pagination')) {
        e.preventDefault();
        const url = e.target.getAttribute('href');

        fetch(url, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
          .then(response => response.text())
          .then(data => {
            container.innerHTML = data;
          })
          .catch(error => console.error('Error:', error));
      }
    });
});

// Changes 24/2/25
// Tagging System
document.addEventListener('DOMContentLoaded', function () { 
    const tagsInput = document.getElementById('id_tags_input');
    const tagsContainer = document.getElementById('tags-container');
    const hiddenTagsInput = document.getElementById('id_tags');

    let tagSuggestionsBox = document.getElementById('tag-suggestions');
    if (!tagSuggestionsBox) {
        tagSuggestionsBox = document.createElement('div');
        tagSuggestionsBox.id = "tag-suggestions";
        tagSuggestionsBox.classList.add('suggestions-box');
        tagsInput.parentNode.appendChild(tagSuggestionsBox);
    }

    let tags = hiddenTagsInput.value && hiddenTagsInput.value !== 'none' 
        ? hiddenTagsInput.value.split(',').map(tag => tag.trim()) 
        : [];

    function updateTagsInput() {
        hiddenTagsInput.value = tags.length > 0 ? tags.join(',') : '';
    }

    function addTag(tag) {
        const normalizedTag = tag.trim().toLowerCase();
        if (tags.includes(normalizedTag)) return;

        const tagDiv = document.createElement('div');
        tagDiv.classList.add('tag', 'badge', 'badge-primary', 'mr-2', 'mb-2', 'p-2');
        tagDiv.style.fontSize = '16px';
        tagDiv.textContent = tag;

        const removeBtn = document.createElement('span');
        removeBtn.classList.add('ml-2');
        removeBtn.style.cursor = 'pointer';
        removeBtn.innerHTML = '&times;';
        removeBtn.onclick = function () {
            removeTag(normalizedTag);
        };

        tagDiv.appendChild(removeBtn);
        tagsContainer.appendChild(tagDiv);

        tags.push(normalizedTag);
        updateTagsInput();
    }

    window.removeTag = function (tag) {
        tags = tags.filter(t => t !== tag);
        updateTagsInput();

        const tagElements = document.querySelectorAll('.tag');
        tagElements.forEach(tagElement => {
            if (tagElement.textContent.toLowerCase().includes(tag)) {
                tagElement.remove();
            }
        });
    };

    tags.forEach(tag => addTag(tag));

    tagsInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ',' || e.key === ' ') {
            e.preventDefault();
            const tag = tagsInput.value.trim();
            if (tag) {
                addTag(tag);
            }
            tagsInput.value = '';
        }
    });

    let suggestionClicked = false; // New flag to track if a suggestion was clicked

    function showTagSuggestions(query) {
        if (query.length === 0) {
            tagSuggestionsBox.style.display = "none";
            return;
        }

        fetch(`/tag_suggestions?q=${query}`)
            .then(response => response.json())
            .then(data => {
                let suggestions = "<ul class='list-group'>";
                data.forEach(tag => {
                    suggestions += `<li class='list-group-item' onclick="selectTag('${tag}')">${tag}</li>`;
                });
                suggestions += "</ul>";
                tagSuggestionsBox.innerHTML = suggestions;
                tagSuggestionsBox.style.display = "block";
            });
    }

    tagsInput.addEventListener('keyup', function () {
        showTagSuggestions(this.value);
    });

    window.selectTag = function (tag) {
        suggestionClicked = true; // Set flag when clicking a suggestion
        tagsInput.value = ''; // Clear the input field
        addTag(tag);
        tagSuggestionsBox.style.display = "none";
    };

    // Prevent the unfinished input from being added when clicking a suggestion
    tagsInput.addEventListener('blur', function () {
        if (suggestionClicked) {
            suggestionClicked = false; // Reset flag to avoid adding typed text
            return;
        }
        const tag = tagsInput.value.trim();
        if (tag) {
            addTag(tag);
        }
        tagsInput.value = '';
    });

    tagSuggestionsBox.addEventListener('mousedown', function () {
        suggestionClicked = true; // Ensure blur event does not trigger unwanted behavior
    });
});


// Toaster Options
toastr.options = {
    "positionClass": "toast-bottom-right",  // Change position to bottom-right
    "timeOut": "5000",                     // Duration the message is visible
    "extendedTimeOut": "1000",              // Time to close when mouse hovers\
    "closeButton": true
  };
setTimeout(function() {
    $(".alert-success").fadeOut("slow", function() {
        $(this).remove();
    });
}, 3000);

$(".save-comment").on('click', function(){
    var _answerid = $(this).data('answer');
    var _comment = $(".comment-text-" + _answerid).val();
    var csrfToken = $('meta[name="csrf-token"]').attr('content'); // Fetch the CSRF token dynamically from the meta tag
    
    // Make sure the comment is not empty
    if(!_comment.trim()) {
        alert("Comment cannot be empty!");
        return;
    }

    var formData = new FormData();
    formData.append('comment', _comment);
    formData.append('answerid', _answerid);
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Append all selected files to the form data
    var files = $("#comment_attachment")[0].files;
    for (var i = 0; i < files.length; i++) {
        formData.append('attachments', files[i]);
    }

    $.ajax({
        url: "/QueryManager/save-comment",
        type: "POST",
        data: formData,
        processData: false,  // Prevent jQuery from automatically transforming the data into a query string
        contentType: false,  // Set content type to false as jQuery will tell the server its a query string request
        beforeSend: function(){
            $(".save-comment").addClass('disabled').text('Saving...');
        },
        success: function(res){
            if(res.bool == true){
                $(".comment-text-" + _answerid).val('');  // Clear the textarea after comment is submitted

                var profilePic = res.profile_picture ? res.profile_picture : "{% static 'profile_pics/default2.jpg' %}";  // Default profile picture if none exists
                var _html = '<div class="card mb-2 comment-item comment-item-' + _answerid + ' animate__animated animate__bounce">\
                    <div class="card-body">\
                        <div class="d-flex align-items-center justify-content-between">\
                            <img src="' + profilePic + '" alt="' + res.username + '" class="rounded-circle answer-profile">\
                            <div class="d-flex flex-column text-left flex-grow-1 ml-2">\
                                <a class="text-decoration-none text-dark" href="#">' + res.username + '</a>\
                                <span class="text-muted" style="font-size: 0.9rem;">' + res.timestamp + '</span>\
                            </div>';

                // Add Delete Button with 'X' icon if applicable
                if(res.can_delete) {
                    _html += '<button type="button" class="btn btn-light btn-sm align-middle" data-toggle="modal" data-target="#deleteCommentModal' + res.comment_id + '" style="font-size: 0.8rem; padding: 2px 6px;">\
                        <i class="fas fa-x"></i>\
                    </button>';
                }

                _html += '</div>\
                        <p class="mt-3">' + _comment + '</p>\
                    </div>';

                _html += '</div>';  // Close the card div

                // Append the newly submitted comment to the correct wrapper
                $(".comment-wrapper-" + _answerid).append(_html);  

                // Update the comment count
                var prevCount = $(".comment-count-" + _answerid).text();
                $(".comment-count-" + _answerid).text(parseInt(prevCount) + 1);  
            }
            $(".save-comment").removeClass('disabled').text('Submit');  // Re-enable the submit button
        },
        error: function(xhr, status, error) {
            console.error("Error:", error);
            alert("An error occurred while submitting your comment.");
        }
    });
});

document.addEventListener("DOMContentLoaded", function() {
    function convertNewlinesToBreaks(elementId) {
        var element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = element.innerHTML.replace(/\n/g, '<br>');
        }
    }
    convertNewlinesToBreaks('quest-detail');
    convertNewlinesToBreaks('answer-solution');
});


// Search Suggestions
function showSuggestions(query) {
    if (query.length == 0) {
        document.getElementById("suggestions").style.display = "none";
        return;
    }

    fetch(`/search_suggestions?q=${query}`)
        .then(response => response.json())
        .then(data => {
            let suggestions = "<ul class='list-group'>";
            data.forEach(item => {
                suggestions += `<li class='list-group-item' onclick="selectSuggestion('${item}')">${item}</li>`;
            });
            suggestions += "</ul>";
            document.getElementById("suggestions").innerHTML = suggestions;
            document.getElementById("suggestions").style.display = "block";
        });
}

function selectSuggestion(suggestion) {
    document.getElementById("search-input").value = suggestion;
    document.getElementById("search-form").submit();
}

document.getElementById("search-input").addEventListener("blur", function() {
    setTimeout(() => {
        document.getElementById("suggestions").style.display = "none";
    }, 200);
});

document.getElementById("search-input").addEventListener("focus", function() {
    if (this.value.length > 0) {
        showSuggestions(this.value);
    }
});

//Glightbox
document.addEventListener('DOMContentLoaded', function() {
    // Find all unique gallery identifiers
    const galleries = document.querySelectorAll('[data-glightbox^="gallery"]');
    const uniqueGalleries = new Set();

    galleries.forEach(gallery => {
        uniqueGalleries.add(gallery.getAttribute('data-glightbox'));
    });

    // Initialize GLightbox for each unique gallery
    uniqueGalleries.forEach(galleryId => {
        GLightbox({
            selector: `[data-glightbox="${galleryId}"]`,
            touchNavigation: true,
            loop: false,
            closeButton: true
        });
    });
});

// Filter tags
document.addEventListener('DOMContentLoaded', function () {
    const filterInput = document.getElementById('filter-tags');
    const tagsContainer = document.getElementById('tags-container');
    const tagItems = tagsContainer.querySelectorAll('.tag-item');

    filterInput.addEventListener('input', function () {
        const query = this.value.toLowerCase();
        tagItems.forEach(item => {
            const tagName = item.getAttribute('data-tag').toLowerCase();
            if (tagName.includes(query)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
});

// Attachment 24/2/25
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll(".remove-attachment").forEach(button => {
        button.addEventListener("click", function () {
            let attachmentId = this.getAttribute("data-attachment-id");
            let attachmentType = this.getAttribute("data-attachment-type"); // New attribute to differentiate

            // Determine the URL based on the attachment type
            let url;
            if (attachmentType === "answer") {
                url = `/remove-attachment/${attachmentId}/`;
            } else if (attachmentType === "comment") {
                url = `/remove-comment-attachment/${attachmentId}/`;
            } else if (attachmentType === "question") {
                url = `/remove-question-attachment/${attachmentId}/`;
            } else {
                console.error("Invalid attachment type");
                return;
            }

            // Get CSRF token from cookie
            function getCSRFToken() {
                let cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i].trim();
                    if (cookie.startsWith("csrftoken=")) {
                        return cookie.split("=")[1];
                    }
                }
                return "";
            }

            // Send a POST request to remove the attachment
            fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(), // Only include the CSRF token
                },
            })
            .then(response => {
                if (response.ok) {
                    return response.json(); // Parse JSON if response is OK
                } else {
                    throw new Error('Error: ' + response.statusText);
                }
            })
            .then(data => {
                if (data.success) {
                    this.parentElement.remove(); // Remove the attachment element from the DOM
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        });
    });
});

