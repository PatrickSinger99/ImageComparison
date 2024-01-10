// Create a menu item with the id "my-menu-item" and the title "Show alert"
browser.menus.create({
  id: "my-menu-item",
  title: "Compare with my library",
  contexts: ["image"] // Only show the menu item on images
});

// Add a listener for when the menu item is clicked
browser.menus.onClicked.addListener((info, tab) => {
  // Check if the clicked menu item is "my-menu-item"
  if (info.menuItemId === "my-menu-item") {
    fetch('http://localhost:5000/compare', { // replace with your Flask server URL and endpoint
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({src: info.srcUrl})
        }).then(response => response.json()).then(data => {
          console.log(data); // log the server response
        }).catch(error => {
          console.log(error);
        });


    /*
    // Fetch the image as a Blob
    fetch(info.srcUrl).then(response => response.blob()).then(blob => {
      // Create a FileReader
      let reader = new FileReader();
      // Add an event listener for when the reading is complete
      reader.addEventListener("load", () => {
        // The result attribute contains the base64 string
        let base64Image = reader.result;

        // Send the base64 string to the Flask server
        fetch('http://localhost:5000/compare', { // replace with your Flask server URL and endpoint
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ image: base64Image, src: info.srcUrl })
        }).then(response => response.json()).then(data => {
          console.log(data); // log the server response
        }).catch(error => {

        });

      });
      // Read the blob as a data URL (base64 string)
      reader.readAsDataURL(blob);
    });
    */
  }
});
