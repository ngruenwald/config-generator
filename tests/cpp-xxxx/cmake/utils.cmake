# converts 'infile' to a unsigned char array named 'label' in 'outfile'
function(xd infile outfile label)
  file(READ ${infile} hexdata HEX)
  string(REGEX REPLACE "(..)" "0x\\1, " formatted ${hexdata})
  file(
    WRITE
    ${outfile}
    "unsigned char ${label}[] = { ${formatted} };\nunsigned long ${label}_size = sizeof(${label});"
  )
endfunction()
