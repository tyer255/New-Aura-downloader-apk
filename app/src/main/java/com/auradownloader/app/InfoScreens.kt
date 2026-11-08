package com.auradownloader.app

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun InfoScreenLayout(
    title: String,
    isDarkMode: Boolean,
    onBack: () -> Unit,
    content: @Composable ColumnScope.(Color, Color) -> Unit
) {
    val textColor = if (isDarkMode) Color.White else Color(0xFF0F172A)
    val subTextColor = if (isDarkMode) Color.White.copy(alpha = 0.65f) else Color(0xFF475569)
    val glassBg = if (isDarkMode) Color.White.copy(alpha = 0.08f) else Color.White.copy(alpha = 0.85f)
    val glassBorder = if (isDarkMode) Color.White.copy(alpha = 0.12f) else Color(0xFFE2E8F0)

    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.Filled.ArrowBack, "Back", tint = textColor) }
            Spacer(modifier = Modifier.width(8.dp))
            Text(title, color = textColor, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        }
        Spacer(modifier = Modifier.height(16.dp))
        
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .clip(RoundedCornerShape(20.dp))
                .background(glassBg)
                .border(1.dp, glassBorder, RoundedCornerShape(20.dp))
                .padding(24.dp)
        ) {
            content(textColor, subTextColor)
        }
    }
}

@Composable
fun InfoSection(title: String, text: String, textColor: Color, subTextColor: Color) {
    Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = textColor)
    Spacer(modifier = Modifier.height(8.dp))
    Text(text, style = MaterialTheme.typography.bodyMedium, color = subTextColor)
    Spacer(modifier = Modifier.height(24.dp))
}

@Composable
fun AboutScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("About Aura Downloader", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("About Us", "Aura Downloader is a premium, fast, and secure media downloading utility.\n\nOur mission is to provide users with a simple and reliable way to save their favorite videos, photos, and audio clips from various social media platforms directly to their devices for offline viewing.\n\nBuilt with modern technologies, our downloader ensures the highest quality media extraction without requiring user registration.", textColor, subTextColor)
    }
}

@Composable
fun PrivacyPolicyScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("Privacy Policy", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("Introduction", "Welcome to Aura Downloader. We respect your privacy and are committed to protecting your personal data. This privacy policy will inform you as to how we look after your personal data when you visit our website.", textColor, subTextColor)
        InfoSection("Data We Collect", "We do not collect any personal data or store any videos you download through our service. The service acts merely as a proxy to fetch public content from supported platforms. All downloads are processed temporarily and are not retained on our servers.", textColor, subTextColor)
        InfoSection("Cookies", "We use local storage strictly for functional purposes, such as remembering your theme preference (Light or Dark mode) and maintaining your recent download history locally on your device. We do not use tracking cookies.", textColor, subTextColor)
        InfoSection("Children's Privacy", "The service is not directed at children under 13 (or applicable minimum age), and does not knowingly collect data from children.", textColor, subTextColor)
        InfoSection("Changes to this Policy", "The policy may be updated from time to time, with the revision date posted on the page.", textColor, subTextColor)
    }
}

@Composable
fun TermsScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("Terms and Conditions", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("Terms", "By accessing this application, you are agreeing to be bound by these Terms and Conditions of Use and agree that you are responsible for the agreement with any applicable local laws.", textColor, subTextColor)
        InfoSection("Use License", "Permission is granted to temporarily download one copy of the materials (information or software) on Aura Downloader for personal, non-commercial transitory viewing only. You must have the legal right to download and use the media you process through this app.", textColor, subTextColor)
        InfoSection("Disclaimer", "The materials on Aura Downloader are provided on an 'as is' basis. We make no warranties, expressed or implied, and hereby disclaim and negate all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.", textColor, subTextColor)
        InfoSection("User Responsibilities", "Users must comply with the Terms of Service of the platform they are downloading from (YouTube, Instagram, Pinterest, TikTok, etc.). Users must not use the service to download, redistribute, or commercially exploit copyrighted material without permission from the rights holder.", textColor, subTextColor)
        InfoSection("Age restriction", "Users must be at least 13 years old (or the minimum legal age in their country) to use this service.", textColor, subTextColor)
        InfoSection("Limitation of Liability", "The service is not liable for any direct, indirect, incidental, or consequential damages arising from use of the service, including copyright or legal claims arising from content downloaded by users.", textColor, subTextColor)
        InfoSection("Modification of Service", "The company reserves the right to modify, suspend, or discontinue the service at any time without prior notice.", textColor, subTextColor)
        InfoSection("Governing Law", "These Terms are governed by the laws of India, and disputes are subject to the exclusive jurisdiction of the courts of Jaipur, India.", textColor, subTextColor)
    }
}

@Composable
fun DMCAScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("DMCA Policy", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("Digital Millennium Copyright Act Notice", "Aura Downloader respects the intellectual property rights of others. We do not host any copyrighted media on our servers. Our tool simply extracts direct links to media files already hosted on public servers of third-party platforms.\n\nIf you are a copyright owner and believe that any content accessed through our service infringes upon your copyrights, please note that we cannot remove content from third-party platforms (like YouTube, TikTok, Instagram, etc.). You must contact the respective platform to have the content removed at the source.\n\nHowever, if you wish to block our tool from processing URLs leading to your copyrighted material, you may send a DMCA notice to our legal/DMCA email address at mridulnareda56@gmail.com, and we will implement filters to prevent downloading from those specific URLs. Please include: identification of the copyrighted work, the specific URL(s) processed through the tool, your contact information, and a good-faith statement.", textColor, subTextColor)
    }
}

@Composable
fun CookiePolicyScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("Cookie Policy", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("What are Cookies?", "Cookies are small text files that are stored on your device when you visit a website. They are widely used to make apps work or improve their efficiency.", textColor, subTextColor)
        InfoSection("How We Use Cookies", "Our service relies on local storage rather than traditional tracking cookies. We use local storage strictly for functional reasons, such as saving your theme preference (Light/Dark mode) and keeping track of your recent downloads locally on your device.", textColor, subTextColor)
        InfoSection("Third-Party Cookies", "We do not use any third-party tracking, advertising, or analytics cookies on this platform. Your data remains private and is not shared with external services.", textColor, subTextColor)
    }
}

@Composable
fun FAQScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("Frequently Asked Questions", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("Is this service free to use?", "Yes, Aura Downloader is 100% free to use with no hidden fees or subscriptions.", textColor, subTextColor)
        InfoSection("Are there any download limits?", "No, you can download as many videos and images as you want.", textColor, subTextColor)
        InfoSection("Why is my download not working?", "Some videos might be private, restricted, or deleted. Make sure the URL is correct and the post is publicly accessible.", textColor, subTextColor)
        InfoSection("Do you store my downloaded files?", "No, we do not store any files on our servers. All processing is done on-the-fly and files are delivered directly to your device.", textColor, subTextColor)
    }
}

@Composable
fun ContactUsScreen(isDarkMode: Boolean, onBack: () -> Unit) {
    InfoScreenLayout("Contact Us", isDarkMode, onBack) { textColor, subTextColor ->
        InfoSection("Get in Touch", "Have questions, suggestions, or experiencing issues with our downloader? We'd love to hear from you.\n\nSupport Channel: For the fastest response, please reach out to us via our official YouTube channel.\n\nYouTube Channel: https://youtube.com/@mridulgaming-_-official-800?si=qsAdamH6-973hgBe\n\nEmail Contact: mridulnareda56@gmail.com\n\nLegal / DMCA inquiries: mridulnareda56@gmail.com", textColor, subTextColor)
    }
}
