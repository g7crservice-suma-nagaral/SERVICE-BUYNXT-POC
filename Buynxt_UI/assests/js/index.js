$(document).ready(function() {
  sID=localStorage.getItem('session_id')
  if (sID ==""){
    window.location.href = "login.html"; 
  }

  // You can set the text inside the <p> tag using jQuery
  $('#li_username').text(localStorage.getItem('userName'));
  fetchFileList()
});

async function generate_imgage(){
    const prompt = document.getElementById("prompt").value;
    if (!prompt) {
      showToast("Please enter a prompt.", "warning");
      return;
    }
    const loader = document.getElementById('loader1');
    loader.style.display = 'block';
    debugger
    try {
      const response = await fetch(`${API_URL}generate-image/`, {
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
    const response = await fetch(`${API_URL}categorize-product/?product_name=${product}`, {
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

async function fn_uploadPdf(){
  const fileInput = document.getElementById('pdfFile');
  const file = fileInput.files[0];

  if (!file) {
    showToast("Please select a file.", "warning");
    return;
  }
  const formData = new FormData();
  formData.append("file", file); 
  
  try {
    // Show loader
    document.getElementById("loader3").style.display = "block";

    // Make the POST request to the FastAPI endpoint
    const response = await fetch(API_URL+"extract-invoice-text", {
      method: "POST",
      headers: {
        'API-Key': localStorage.getItem('session_id')
    },
      body: formData,
    });

    // Handle the response
    debugger
    if (response.ok) {
      const result = await response.json();
      
      // Display the raw JSON response in the UI
      // document.getElementById('jsonResponse').textContent = JSON.stringify(result, null, 2);
      // document.getElementById('jsonSection').style.display = 'block';
     
      // document.getElementById('downloadLink').href = dummyResponse.filePath;
      document.getElementById('downloadSection').style.display = 'block';
    } else {
      showToast("File upload failed:  " + response.statusText, "error");
    }
  } catch (error) {
    console.error("Error uploading file:", error);
    showToast("An error occurred while uploading the file.", "error");
  } finally {
    // Hide loader
    document.getElementById("loader3").style.display = "none";
  }

}

async function fetchFileList() {
  const loader = document.getElementById("loader4");
  loader.style.display = "block";
  const response = await fetch(`${API_URL}get_file_list`, {
    method: "GET",
    headers: {
      "Content-type": "application/json; charset=UTF-8",
      "API-Key": localStorage.getItem("session_id"),
    },
  });

  const data = await response.json();

  const tableBody = document.getElementById("fileTableBody");
  tableBody.innerHTML = ""; // Clear existing rows

  data.files.forEach((file) => {
    const row = document.createElement("tr");

    const slNoCell = document.createElement("td");
    slNoCell.textContent = file.sl_no;

    const pdfFileCell = document.createElement("td");
    const pdfLink = document.createElement("a");
    pdfLink.textContent = file.pdf_file;
    pdfLink.href = `${API_URL}download_blob_file?file_name=${file.pdf_file}`;
    pdfLink.target = "_blank";
    pdfFileCell.appendChild(pdfLink);

    const jsonFileCell = document.createElement("td");
    if (file.json_file) {
      const jsonLink = document.createElement("a");
      jsonLink.textContent = file.json_file;
      jsonLink.href = `${API_URL}download_blob_file?file_name=${file.json_file}`;
      jsonLink.target = "_blank";
      jsonFileCell.appendChild(jsonLink);
    } else {
      jsonFileCell.textContent = "N/A";
    }

    row.appendChild(slNoCell);
    row.appendChild(pdfFileCell);
    row.appendChild(jsonFileCell);

    tableBody.appendChild(row);
  });
  loader.style.display = "none";
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