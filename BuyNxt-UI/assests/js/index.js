$(document).ready(function() {
  // You can set the text inside the <p> tag using jQuery
  $('#li_username').text(localStorage.getItem('userName'));
});

async function generate_imgage(){
    const prompt = document.getElementById("prompt").value;
    if (!prompt) {
      showToast("Please enter a prompt.", "warning");
      return;
    }
    const loader = document.getElementById('loader1');
    loader.style.display = 'block';
    try {
      const response = await fetch(`${API_URL}generate-image`, {
          method: 'POST',
          body: JSON.stringify({
            "prompt": prompt
          }),
          headers: {
              'Content-type': 'application/json; charset=UTF-8',
              'API-Key': localStorage.getItem('session_id')
          }
      });
      const responseData = await response.json();
      debugger;
      if (!response.ok) {
          showToast(responseData.message || "Something went wrong!!! Please try again later.", "error");
          return;
      }

      // Simulate API call to generate an image
      const generatedImageUrl = responseData.image_url

      // Update the image container
      const imageContainer = document.getElementById("imageContainer");
      const generatedImage = document.getElementById("generatedImage");
      generatedImage.src = generatedImageUrl;
      imageContainer.style.display = "block";

      // Handle download button
      //const downloadBtn = document.getElementById("downloadBtn");
      
      document.getElementById('downloadBtn').addEventListener('click', () => {
        fetch(generatedImageUrl)
            .then(response => response.blob()) // Fetch image as blob
            .then(blob => {
                const blobUrl = window.URL.createObjectURL(blob); // Create blob URL
                const link = document.createElement('a'); // Create temporary anchor tag
                link.href = blobUrl; 
                link.download = 'generated_image.png'; // Suggested download filename
                document.body.appendChild(link); // Add to DOM
                link.click(); // Trigger download
                document.body.removeChild(link); // Clean up
                window.URL.revokeObjectURL(blobUrl); // Revoke blob URL
            })
            .catch(error => {
                console.error('Error downloading the image:', error);
            });
    });

    } catch (error) {
      showToast("An error occurred: " + error.message, "error");
    }finally {
      // Hide loader
      document.getElementById("loader1").style.display = "none";
    }

}

async function regenerate_image() {
  const imageElement = document.getElementById('generatedImage');
  const imageContainer = document.getElementById('imageContainer');
        
  // Clear the image source
  imageElement.src = '';
  imageElement.alt = 'Image Removed';

  // Optionally hide the image container
  imageContainer.style.display = 'none';
  generate_imgage()
}

async function clear_imgage() {
  const imageElement = document.getElementById('generatedImage');
  const imageContainer = document.getElementById('imageContainer');
        
  // Clear the image source
  imageElement.src = '';
  imageElement.alt = 'Image Removed';

  // Optionally hide the image container
  imageContainer.style.display = 'none';
}
    // // Handle regenerate button
    // const regenerateBtn = document.getElementById("regenerateBtn");
    // regenerateBtn.addEventListener("click", () => {
    //   alert("Regenerate functionality to be implemented.");
    // });



async function get_category(){
  const product = document.getElementById("product-name").value;
  if (!product) {
    showToast("Please enter a product.", "warning");
    return;
  }
  const loader = document.getElementById('loader2');
  loader.style.display = 'block';
  try {
    const response = await fetch(`${API_URL}categorize-product?product_name=${product}`, {
        method: 'GET',
        headers: {
            'Content-type': 'application/json; charset=UTF-8',
            'API-Key': localStorage.getItem('session_id')
        }
    });
    const responseData = await response.json();

    
    debugger;
    if (!response.ok) {
        showToast(responseData.message || "Something went wrong!!! Please try again later.", "error");
        return;
    }

    // Select the div to insert product details
    const productInfoDiv = document.getElementById('product-info');

    // Initialize an empty string to hold the formatted HTML content
    let productDetailsHTML = '';

    // Iterate through the responseData object and generate HTML for each key-value pair
    for (const key in responseData) {
        if (responseData.hasOwnProperty(key)) {
            const value = responseData[key];
            productDetailsHTML += `<p><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</p>`;
        }
    }

    // Insert the generated HTML content into the product-info div
    productInfoDiv.innerHTML = productDetailsHTML;

    // document.getElementById('product-info').innerHTML = productInfo;
     document.getElementById('product_result').style.display = 'block';

  } catch (error) {
    showToast("An error occurred: " + error.message, "error");
  }finally {
    // Hide loader
    document.getElementById("loader2").style.display = "none";
  }

}

const userButton = document.getElementById('userButton');
const dropdownContent = document.getElementById('dropdownContent');

userButton.addEventListener('click', () => {
  dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
});

// Hide dropdown when clicking outside
document.addEventListener('click', (event) => {
  if (!userButton.contains(event.target) && !dropdownContent.contains(event.target)) {
    dropdownContent.style.display = 'none';
  }
});
  
function btn_logout(){
  localStorage.removeItem("userName")
  window.location.href = "login.html";
}