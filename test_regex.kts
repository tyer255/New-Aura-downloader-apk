val timeRegex = Regex("""\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]""")
println(timeRegex.findAll("[00:15.50]").toList().size)
