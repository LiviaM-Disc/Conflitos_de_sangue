# Execution contract for updated GDD

## Reference and evidence
The user's attached document controls this edit: C:\Users\lb119\Downloads\GDD (1).docx.
SHA256 d6b7eae200b89f1372ec664d9a826fcc4993a7ebf5d87f9093501df8b64283d4.
It supersedes the older retained GDD reference for content and appearance. Both references remain unchanged.
Source has 12 rendered A4 pages, one portrait section, nine tables, 11 screenshots.
Evidence: source-outline.txt, source-inventory.json, source-render/source.pdf and page-1.png through page-12.png, all visually inspected.
No headers, footers, fields, content controls, text boxes or footnotes. Images are all in section 8.
Renderer unavailable because the Windows runtime contains no LibreOffice. Read-only Microsoft Word export plus bundled Poppler supplies equivalent page QA. No third-party desktop LibreOffice is used.

## Page and typography
A4 11906 by 16838 twips. Margins 566.9291338582677 twips (1 cm), header/footer distance 720 twips. One section, page numbering starts at 1, no displayed page numbers.
Arial 11 pt default, black, 1.15 line spacing. Main title centered bold 20 pt. Section headings bold 14 pt; subsection headings bold 12 pt. Source uses a mixture of Heading1/Title/normal for headings; normalize semantic roles while keeping visual sizes. Body explanatory text justified; short fields left aligned. Preserve the simple black and white design.
Tables use black headers with white text, white body cells, black gridlines, approximately 5 pt padding, fixed column grid and auto-height rows. Clone source two/three-column structures, adjust column proportions for updated content; add repeating headers and prevent split rows.
Source screenshots have inconsistent widths and no captions. Replace obsolete screens with current supplied local captures, fit proportionally in the same section, two per page with concise captions. No invented or altered screenshots.

## Slot map and permitted content changes
All body text is editable to reflect the implemented eight-stage campaign; preserve the author's name. Ordered sections remain: 1 Identification (including characters), 2 Story, 3 Story progression, 4 Gameplay, 5 Interface and controls, 6 Art direction, 7 Technical description, 8 Screenshots.
Original paragraph and table indices recorded in source-outline.txt are stable locators for original slots. Each full section is a rewrite slot; insert eight stage details and update tables by cloning original row patterns. Remove obsolete duplicate summaries, blank paragraphs used for spacing, old keyboard movement controls, Fibonacci, final resolution claims, obsolete file tree and old screenshot slots. Document current points, local Django/SQLite ranking, save-versus-end behavior and characters' roles.
Page count may grow with eight stages and missing ranking documentation; adjust flow through keep-with-next and source-derived page breaks, not by reducing text size.

## Package preservation
source-inventory.json records all package parts, sizes and hashes. Only word/document.xml is edited, plus the existing screenshot media parts selected for replacement. All styles, numbering, relationships, settings, metadata, themes and other parts are preserved byte for byte. Reuse image relationships, retaining unused media/relations to avoid unrelated edits. New screenshots replace existing PNG media bytes. Keep section properties unchanged. First title gets Word Title style via body markup, no style-part change required.
Final gates: matching untouched part hashes, unchanged source hash, exactly one section with original geometry, eight current phase titles, score/ranking text matching source code, all final pages visually checked with no table split defects, orphan headings, clipped content or incorrect images.
