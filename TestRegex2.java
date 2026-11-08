import java.util.regex.*;

public class TestRegex2 {
    public static void main(String[] args) {
        Pattern p2 = Pattern.compile("\\[(\\d{1,3}):(\\d{1,2})(?:[:.](\\d{1,3}))?]"); // With ?
        Matcher m3 = p2.matcher("[00:15]");
        System.out.println("Match 2 [00:15] (with ?): " + m3.find());
        
        Pattern p3 = Pattern.compile("\\[(\\d{1,3}):(\\d{1,2})(?:[:.](\\d{1,3}))]"); // Without ?
        Matcher m4 = p3.matcher("[00:15]");
        System.out.println("Match 3 [00:15] (without ?): " + m4.find());
    }
}
