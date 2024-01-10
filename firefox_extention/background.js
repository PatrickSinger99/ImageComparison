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
    // Get the image URL from the info object
    let imageUrl = info.srcUrl;

    // Download image
    browser.downloads.download({
        url: imageUrl,
        filename: "image_comparison_obj.jpg"
      });
  }
});

// Not used currently
function getBase64Image(img) {
    // Create an empty canvas element
    var canvas = document.createElement("canvas");
    canvas.width = img.width;
    canvas.height = img.height;

    // Copy the image contents to the canvas
    var ctx = canvas.getContext("2d");
    ctx.drawImage(img, 0, 0);

    // Get the data-URL formatted image
    // Firefox supports PNG and JPEG. You could check img.src to
    // guess the original format, but be aware the using "image/jpg"
    // will re-encode the image.
    var dataURL = canvas.toDataURL("image/png");

    return dataURL.replace(/^data:image\/(png|jpg);base64,/, "");
}