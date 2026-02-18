function Str(el)
  -- This regex looks for digits followed by st, nd, rd, or th
  -- %d matches a digit, %a matches letters
  local start, finish, num, ordinal = el.text:find("(%d+)([snrt][tdh])")
  
  if start then
    -- We split the string: part before, the superscript part, part after
    return {
      pandoc.Str(el.text:sub(1, start + #num - 1)),
      pandoc.Superscript(ordinal),
      pandoc.Str(el.text:sub(finish + 1))
    }
  end
end