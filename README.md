# Mikro Integration Demo

A demonstration application for businesses seeking to integrate with the Mikro software infrastructure. This project showcases how to retrieve order information from a relational database and format it appropriately for transmission to the Mikro software platform.

## Overview

This application serves as a practical example for companies looking to implement integration with Mikro's software infrastructure. The demo scenario demonstrates the process of:

- Retrieving order data from a relational database
- Formatting the data according to Mikro software specifications
- Transmitting the formatted data to the Mikro platform

## Requirements

- Python 3.9+
- Access to a relational database containing order information
- Valid Mikro software credentials (API key, user code, company code)

## Installation

### Option 1: Using Pre-built Executable

1. Download the latest `.exe` file from the [GitHub Actions releases](https://github.com/hselimtuna/mikro-integration-demo/actions)
2. Configure the required environment variables (see Configuration section below)
3. Run the executable

### Option 2: Running from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/hselimtuna/mikro-integration-demo.git
   cd mikro-integration-demo
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the required environment variables (see Configuration section below)
4. Run the application

## Configuration

The application requires the following environment variables to be set on your system:

| Variable | Description |
|----------|-------------|
| `DB_HOST` | Your database host address |
| `DB_PORT` | Your database port number |
| `DB_NAME` | Your database name |
| `DB_USER` | Your database username |
| `DB_PASS` | Your database password |
| `KULLANICI_KODU` | Your Mikro user code |
| `API_KEY` | Your Mikro API key |
| `FIRMA_KODU` | Your Mikro company code |

### Setting Environment Variables

**Windows:**
1. Open System Properties → Advanced → Environment Variables
2. Add each variable with its corresponding value

**Linux/macOS:**
```bash
export DB_HOST=your_db_host
export DB_PORT=your_db_port
export DB_NAME=your_db_name
export DB_USER=your_db_user
export DB_PASS=your_db_pass
export KULLANICI_KODU=your_mikro_user_code
export API_KEY=your_mikro_api_key
export FIRMA_KODU=your_mikro_company_code
```

## Usage

Once configured, the application will automatically:
1. Connect to your specified database
2. Retrieve order information
3. Format the data for Mikro software compatibility
4. Transmit the data to the Mikro platform

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as a demonstration for integration purposes.

## Support

For questions or issues related to Mikro software integration, please refer to the official Mikro documentation or contact their support team.