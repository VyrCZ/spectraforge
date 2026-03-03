-- Filter to prevent "orphans" (short words at the end of a line)
function Inlines (is)
  for i = 1, #is - 1 do
    -- If the current element is a short word (1 or 2 characters)
    -- AND the next element is a regular space...
    if is[i].t == 'Str' and #is[i].text <= 2 and is[i+1].t == 'Space' then
      -- Replace the regular space with a non-breaking space
      is[i+1] = pandoc.Str('\u{00a0}')
    end
  end
  return is
end