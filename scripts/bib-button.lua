-- Helper to identify labels and colors based on URL
local function get_label(url)
  url = url:lower()
  if url:match("hal%.science")  or url:match("hal%.inria")  or url:match("archives%-ouvertes") then
    return "HAL", "btn-hal"
  elseif url:match("bioarxiv") then
    return "BIORXIV", "btn-hal"
  elseif url:match("arxiv") then
    return "ARXIV", "btn-hal"
  elseif url:match("%.pdf$") or url:match("download") then
    return "PDF", "btn-pdf"
  elseif url:match("github%.com") then
    return "GITHUB", "btn-code"
  elseif url:match("elife") or
         url:match("rstb") or
         url:match("eneuro") or
         url:match("zenodo") or
         url:match("fninf") or
         url:match("fncom") or
         url:match("peerj") then
    return "DOI", "btn-doi-green"
  elseif url:match("doi%.org") then
    return "DOI", "btn-doi"
  else
    return "LINK", "btn-link"
  end
end

-- Helper function to check if a class exists
local function has_class(el, target_class)
  if el.classes then
    for _, class in ipairs(el.classes) do
      if class == target_class then return true end
    end
  end
  return false
end

function Div(el)
  -- Check for bibliography entry class
  if has_class(el, 'csl-entry') then
    return pandoc.walk_block(el, {
      Link = function(link)
        local label, class = get_label(link.target)
        local text = pandoc.utils.stringify(link.content)
        
        -- If it's a raw URL or a CSL-generated label, turn it into a button
        if not text:find(" ") or text:match("^https?://") or text:match("DOI") or text:match("URL") then
          link.attributes['class'] = 'btn-bib ' .. class
          link.content = {pandoc.Str("#" .. label)}
          return link
        end
      end,
      
      Str = function(s)
        -- Remove the "URL:" or "URL" prefix and any trailing colons
        if s.text:match("^URL:?$") or s.text == "URL" then
          return {}
        end
      end
    })
  end
end
