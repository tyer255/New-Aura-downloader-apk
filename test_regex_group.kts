val timeRegex = Regex("""\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]""")
val match = timeRegex.find("[00:15]")
if (match != null) {
    println("Groups size: ${match.groupValues.size}")
    println("Group 3: '${match.groupValues[3]}'")
} else {
    println("No match")
}
