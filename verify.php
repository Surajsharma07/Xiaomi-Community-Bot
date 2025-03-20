<?php
// User Verification Form Handler
require 'vendor/autoload.php';

use Google\Client;
use Google\Service\Sheets;

function saveToGoogleSheet($data) {
    $serviceAccountFile = 'xiaomi-mi-community-ee216fa709be.json';  // Path to your service account file
    $spreadsheetId = '1vBff9gf2lEw2sJD8wWuNB98SZa8AqQqszvn6YCTqWqY';        // Google Sheets Spreadsheet ID
    $sheetName = 'userData';                         // Name of the sheet (default: Sheet1)

    // Create Google Client
    $client = new Client();
    $client->setAuthConfig($serviceAccountFile);
    $client->addScope([Sheets::SPREADSHEETS]);

    // Create Sheets Service
    $service = new Sheets($client);

    // Data to append (as rows)
    $values = [array_values($data)];
    $body = new Sheets\ValueRange(['values' => $values]);

    // Append data to the sheet
    $params = ['valueInputOption' => 'USER_ENTERED'];
    $range = $sheetName . '!A1'; // Starting cell

    $service->spreadsheets_values->append($spreadsheetId, $range, $body, $params);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Prepare data to send to Telegram bot
    $user_id = $_POST['user_id'] ?? null;
    $group_id = $_POST['group_id'] ?? null;
    $message_id = $_POST['message_id'] ?? null; // Fetch message_id from POST
    $name = $_POST['name'] ?? null;
    $email = $_POST['email'] ?? null;
    $telegram_username = $_POST['telegram_username'] ?? null;
    $mi_id = $_POST['mi_id'] ?? null;
    $country = $_POST['country'] ?? null;
    $dob = $_POST['dob'] ?? null;
    $reason_to_join = $_POST['reason_to_join'] ?? null;
    $terms_accepted = isset($_POST['terms_accepted']) ? filter_var($_POST['terms_accepted'], FILTER_VALIDATE_BOOLEAN) : false;

    if ($user_id && $group_id && $message_id && $terms_accepted) {
        // Fetch the group name from Telegram API
        $telegramToken = "862689552:AAGIHi7HAulHHlEmhFube5zXexG8UtvB0Xs"; // Use the same bot token
        $group_info_url = "https://api.telegram.org/bot{$telegramToken}/getChat?chat_id={$group_id}";

        $ch = curl_init($group_info_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $group_info_response = curl_exec($ch);
        curl_close($ch);

        $group_name = "Your Awesome Group"; // Default group name
        if ($group_info_response) {
            $group_info = json_decode($group_info_response, true);
            if (isset($group_info['ok']) && $group_info['ok'] && isset($group_info['result']['title'])) {
                $group_name = $group_info['result']['title'];
            }
        }

        // Construct the message to send to the bot
        $message = "🎉 Woohoo! You've been verified! 🎉\n";
        $message .= "Welcome to the Group - {$group_name}!\n";

        $bot_url = "https://api.telegram.org/bot{$telegramToken}/sendMessage";
        $payload = [
            'chat_id' => $user_id,
            'text' => $message
        ];

        $ch = curl_init($bot_url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);

        // Delete the welcome message from the chat
        $delete_message_url = "https://api.telegram.org/bot{$telegramToken}/deleteMessage";
        $delete_payload = [
            'chat_id' => $group_id,
            'message_id' => $message_id
        ];

        $ch = curl_init($delete_message_url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($delete_payload));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $delete_response = curl_exec($ch);
        curl_close($ch);

        // Unmute the user in Telegram
        $unmute_url = "https://api.telegram.org/bot{$telegramToken}/restrictChatMember";
        $payload = [
            'chat_id' => $group_id,
            'user_id' => $user_id,
            'permissions' => [
                'can_send_messages' => true,
                'can_send_media_messages' => true,
                'can_send_polls' => true,
                'can_send_other_messages' => true,
                'can_add_web_page_previews' => true,
                'can_change_info' => false,
                'can_invite_users' => false,
                'can_pin_messages' => false
            ]
        ];

        $ch = curl_init($unmute_url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $unmute_response = curl_exec($ch);
        curl_close($ch);
        // Display success message

        // Silent Google Sheets data save
        // Collect form data
    $formData = [
        'User ID' => $user_id,
        'Telegram Username' => $telegram_username,
        'Email' => $email,
        'Mi ID' => $mi_id,
        'Country' => $country,
        'DOB' => $dob,
        'Reason to Join' => $reason_to_join,
        'Timestamp' => date('Y-m-d H:i:s')
    ];

    saveToGoogleSheet($formData);
        $success_message = "You have been verified & unmuted! Please close the web app.";
    } else {
        // Handle missing user_id, group_id, message_id, or terms not accepted
        $error_message = "User ID, Group ID, Message ID, and acceptance of terms are required.";
    }
}

// Extract user_id, group_id, and message_id from the query string
$user_id = $_GET['user_id'] ?? '';
$group_id = $_GET['group_id'] ?? '';
$message_id = $_GET['message_id'] ?? ''; // Fetch message_id from GET

// Fetch the group name from Telegram API for display in the form
$group_name = "Your Awesome Group"; // Default group name
$telegram_username = ""; // Default username
if ($user_id) {
    $telegramToken = "862689552:AAGIHi7HAulHHlEmhFube5zXexG8UtvB0Xs";
    $user_info_url = "https://api.telegram.org/bot{$telegramToken}/getChat?chat_id={$user_id}";

    $ch = curl_init($user_info_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $user_info_response = curl_exec($ch);
    curl_close($ch);

    if ($user_info_response) {
        $user_info = json_decode($user_info_response, true);
        if (isset($user_info['ok']) && $user_info['ok'] && isset($user_info['result']['username'])) {
            $telegram_username = $user_info['result']['username'];
        }
    }
}

if ($group_id) {
    $group_info_url = "https://api.telegram.org/bot{$telegramToken}/getChat?chat_id={$group_id}";

    $ch = curl_init($group_info_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $group_info_response = curl_exec($ch);
    curl_close($ch);

    if ($group_info_response) {
        $group_info = json_decode($group_info_response, true);
        if (isset($group_info['ok']) && $group_info['ok'] && isset($group_info['result']['title'])) {
            $group_name = $group_info['result']['title'];
        }
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Verification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f4f4f9;
            overflow: hidden;
        }
        .container {
            text-align: center;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
        p {
            color: #555;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        label {
            font-weight: bold;
            color: #555;
            font-size: 0.9rem;
        }
        input[type="text"],
        input[type="email"],
        textarea,
        select,
        button {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 0.9rem;
        }
        button {
            background-color: #007BFF;
            color: #fff;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            padding: 10px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .success-message {
            color: #28a745;
            font-size: 1rem;
            margin-top: 20px;
        }
        .error-message {
            color: #dc3545;
            font-size: 1rem;
            margin-top: 20px;
        }
        @media (max-width: 600px) {
            .container {
                padding: 15px;
            }
            h1 {
                font-size: 1.2rem;
            }
            button {
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>User Verification Form</h1>
        <?php if (isset($success_message)): ?>
            <p class="success-message"><?php echo htmlspecialchars($success_message); ?></p>
        <?php elseif (isset($error_message)): ?>
            <p class="error-message"><?php echo htmlspecialchars($error_message); ?></p>
        <?php else: ?>
            <form method="POST" action="">
                <input type="hidden" id="user_id" name="user_id" value="<?php echo htmlspecialchars($user_id); ?>" required>
                <input type="hidden" id="group_id" name="group_id" value="<?php echo htmlspecialchars($group_id); ?>" required>
                <input type="hidden" id="message_id" name="message_id" value="<?php echo htmlspecialchars($message_id); ?>" required> <!-- Include message_id -->
                <input type="hidden" id="group_name" name="group_name" value="<?php echo htmlspecialchars($group_name); ?>" required>
                
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" placeholder="Enter your name" value="<?php echo htmlspecialchars($name ?? ''); ?>" required>

                <label for="email">Email:</label>
                <input type="email" id="email" name="email" placeholder="Enter your email address" required>

                <label for="telegram_username">Telegram Username:</label>
                <input type="text" id="telegram_username" name="telegram_username" value="@<?php echo htmlspecialchars($telegram_username); ?>" readonly required>

                <label for="mi_id">Mi ID:</label>
                <input type="number" id="mi_id" name="mi_id" placeholder="Enter Mi community ID" required>

                <label for="country">Country:</label>
                <input type="text" id="country" name="country" required>

                <label for="dob">DOB:</label>
                <input type="date" id="dob" name="dob" required>

                <label for="reason_to_join">Reason to Join the Group:</label>
                <textarea id="reason_to_join" name="reason_to_join" rows="4" required></textarea>

                <label>
                    <input type="checkbox" id="terms_accepted" name="terms_accepted" value="true" required>
                    I accept the terms and conditions
                </label>

                <button type="submit">Submit</button>
            </form>
        <?php endif; ?>
    </div>
</body>
</html>