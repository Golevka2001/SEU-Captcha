package org.example;

import java.io.File;
import java.io.FileOutputStream;

import com.pig4cloud.captcha.ArithmeticCaptcha;
import com.pig4cloud.captcha.base.Captcha;

class Main {

    /**
     * Generate arithmetic captcha, similar to those used in
     * http://newxk.urp.seu.edu.cn/
     *
     * @param imagesPath Path to `images/`
     * @param labelPath Path to `labels.txt`
     */
    public static void genArithmeticCaptcha(String imagesPath, String labelPath) {
        try {
            // Generate captcha
            ArithmeticCaptcha captcha = new ArithmeticCaptcha(111, 36);
            // Set random font style (Font.PLAIN, Font.BOLD, Font.ITALIC) & font size (32+-4)
            int fontStyle = (int) (Math.random() * 3);
            int fontSize = 32 + (int) (Math.random() * 9) - 4;
            captcha.setFont(Captcha.FONT_1, fontStyle, fontSize);
            captcha.setLen(3); // 3 integers
            captcha.supportAlgorithmSign(4); // 4 represents +, -, x
            captcha.setDifficulty(10); // upper bound of the integers

            String label = captcha.getArithmeticString(); // expression
            // String result = captcha.text(); // result
            // System.out.println("label: " + label);

            // Calculate hash as filename
            String base64 = captcha.toBase64();
            String hash = Integer.toHexString(base64.hashCode());

            // Drop duplicates
            File imageFile = new File(imagesPath + hash + ".png");
            if (imageFile.exists()) {
                return;
            }

            // Save
            FileOutputStream imageFos = new FileOutputStream(imageFile);
            FileOutputStream labelFos = new FileOutputStream(labelPath, true);
            try (imageFos; labelFos) {
                captcha.out(imageFos);
                labelFos.write((hash + ".png\t" + label + "\n").getBytes());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Generate arithmetic captcha and save
     *
     * @param args[0] loopCount Number of captcha to generate
     * @param args[1] imagesPath Path to `images/`
     * @param args[2] labelPath Path to `labels.txt`
     */
    public static void main(String[] args) {
        int loopCount = 1;
        String imagesPath = "./dataset/images";
        String labelPath = "./dataset/labels.txt";

        // Parse arguments
        if (args.length > 0) {
            loopCount = Integer.parseInt(args[0]);
        }
        if (args.length > 1) {
            imagesPath = args[1];
        }
        if (args.length > 2) {
            labelPath = args[2];
        }

        // Check
        if (!imagesPath.endsWith(File.separator)) {
            imagesPath += File.separator;
        }
        File imagesDir = new File(imagesPath);
        if (!imagesDir.exists()) {
            imagesDir.mkdirs();
        }
        File labelFile = new File(labelPath);
        if (!labelFile.exists()) {
            try {
                labelFile.createNewFile();
            } catch (Exception e) {
                e.printStackTrace();
                return;
            }
        }

        for (int i = 0; i < loopCount; i++) {
            genArithmeticCaptcha(imagesPath, labelPath);
            System.out.println((i + 1) + " / " + loopCount);
        }
    }
}
