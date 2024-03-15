{
  description = "cursorgen is a fork of win2xcur that aims to preserve the image quality of the cursor.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    pre-commit-hooks-nix.url = "github:cachix/pre-commit-hooks.nix";
    devshell.url = "github:numtide/devshell";
  };

  outputs = {
    self,
    pre-commit-hooks-nix,
    ...
  } @ inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      systems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
      imports = [inputs.flake-parts.flakeModules.easyOverlay];
      perSystem = {
        config,
        system,
        pkgs,
        ...
      }: {
        _module.args.pkgs = import inputs.nixpkgs {
          inherit system;
          overlays = [
            inputs.devshell.overlays.default
          ];
        };
        checks = {
          pre-commit-check = pre-commit-hooks-nix.lib.${system}.run {
            src = ./.;
            hooks = {
              alejandra.enable = true; # enable pre-commit formatter
              black.enable = true;
              flake8.enable = true;
              isort.enable = true;
            };
            settings = {
              alejandra = {
                package = config.formatter;
                check = true;
                threads = 4;
              };
              isort = {
                profile = "black";
              };
            };
          };
        };
        devShells.default = let
          inherit (config.checks.pre-commit-check) shellHook;
        in
          pkgs.devshell.mkShell {
            imports = [(pkgs.devshell.importTOML ./devshell.toml)];
            git.hooks = {
              enable = true;
              pre-commit.text = shellHook;
            };
            packages = with pkgs; [
              (python3.withPackages (p:
                with p; [
                  wand
                  numpy
                  pillow
                  toml
                  black
                  flake8
                  isort
                ]))
            ];
          };
        formatter = pkgs.alejandra;
      };
    };
}
