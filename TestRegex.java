import java.util.regex.*;

public class TestRegex {
    public static void main(String[] args) {
        Pattern p = Pattern.compile("\\[(\\d{1,3}):(\\d{1,2})(?:[:.](\\d{1,3}))?\\]");
        Matcher m1 = p.matcher("[00:15]");
        System.out.println("Match [00:15]: " + m1.find());
        
        Matcher m2 = p.matcher("[00:15.50]");
        System.out.println("Match [00:15.50]: " + m2.find());
        if (m2.reset().find()) {
           System.out.println("Group 3 length: " + (m2.group(3) != null ? m2.group(3).length() : "null"));
           System.out.println("Group 3: " + m2.group(3));
        }
    }
}
