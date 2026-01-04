# Contributing to MuxOS

Thank you for your interest in contributing to MuxOS! This document provides guidelines for contributing.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported
2. Use the bug report template
3. Include:
   - System information (`neofetch`)
   - Hardware details (`lspci`)
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant logs (`journalctl -xe`)

### Suggesting Features

1. Check if the feature has been suggested
2. Describe the feature clearly
3. Explain the use case
4. Consider implementation complexity

### Code Contributions

#### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd MuxOS

# Install build dependencies
sudo apt install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    git \
    build-essential

# Build ISO
sudo ./scripts/build-iso.sh

# Test in VM
./scripts/test-vm.sh
```

#### Code Style

**Shell Scripts:**
- Use `#!/bin/bash` shebang
- 4 spaces for indentation
- Use meaningful variable names
- Add comments for complex logic
- Use `set -e` for error handling

**Python:**
- Follow PEP 8
- Use 4 spaces for indentation
- Add docstrings for functions
- Use type hints where appropriate

**Configuration Files:**
- Use consistent formatting
- Add comments explaining options
- Keep organized and readable

#### Commit Messages

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat: Add NVIDIA driver auto-detection

Implement automatic detection of NVIDIA GPUs and prompt
user to install proprietary drivers for better performance.

Closes #123
```

#### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

**PR Checklist:**
- [ ] Code follows style guidelines
- [ ] Changes are tested
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

### Testing

#### Manual Testing

1. Build ISO with your changes
2. Test in VM first
3. Test on real hardware if possible
4. Test different scenarios:
   - Fresh installation
   - Upgrade from previous version
   - Different hardware configurations

#### Test Cases

- Boot process
- Desktop environment
- Hardware detection
- Driver installation
- Gaming performance
- Application functionality
- System stability

### Documentation

#### What to Document

- New features
- Configuration changes
- Installation steps
- Troubleshooting tips
- API changes

#### Documentation Style

- Clear and concise
- Use examples
- Include screenshots where helpful
- Keep updated with code changes

### Areas Needing Contribution

#### High Priority
- Graphical installer
- Automated testing
- Hardware compatibility database
- Performance benchmarks
- Translation support

#### Medium Priority
- Additional themes
- More pre-configured games
- Backup/restore tools
- System monitoring improvements
- Power management

#### Low Priority
- Easter eggs
- Additional wallpapers
- Icon themes
- Sound themes

## Project Structure

```
MuxOS/
├── apps/              # Custom applications
├── boot/              # Bootloader configuration
├── config/            # System configuration
├── desktop/           # Desktop environment configs
├── docs/              # Documentation
├── scripts/           # Build and utility scripts
├── system/            # System components
│   ├── drivers/       # Driver installation scripts
│   ├── init/          # Init system
│   ├── kernel/        # Kernel configuration
│   ├── optimizations/ # Performance tweaks
│   └── services/      # System services
└── README.md
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on the project goals
- Help others learn

### Communication

- Use clear, professional language
- Stay on topic
- Be patient with responses
- Share knowledge
- Credit others' work

## Getting Help

- Read documentation first
- Search existing issues
- Ask in discussions
- Be specific about problems
- Provide context

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for questions about contributing!

---

**Thank you for making MuxOS better! 🚀**
