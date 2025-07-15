<h1><b>GBB Tool</b></h1>

Tool for viewing and editing .gbb files used in Brian Lara Cricket '99 / Shane Warne Cricket '99.

<b>✅ Features</b>

<ul>
  <li>
  🔍 Decode .GBB files into viewable 32-bit BMP images.
    
  </li><li>
  🖼️ Re-encode edited BMPs back into the .GBB format with original compression preserved.
    
  </li><li>
  📐 Correct aspect ratios for non-square and stretched textures.
    
  </li><li>
  🖱️ Drag-and-drop support, file association, and metadata viewing.
    
  </li>
</ul>


<b>📦 Format Details</b>

.GBB files store raw 24-bit textures using:

<ul>
  <li>
    Run-Length Encoding (RLE) or 
  </li>
  <li>
    Bit-packed delta compression
  </li>
</ul>
<br>
The texture dimensions are stored at the beginning of the file. This tool reverse-engineers that logic to allow safe texture replacement without corrupting the original file.
