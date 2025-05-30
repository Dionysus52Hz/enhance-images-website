import {
   Pill,
   Tablets,
   Store,
   Factory,
   UsersRound,
   UserRoundPen,
   History,
   Contact,
   FileInput,
   FileOutput,
   ChartNoAxesCombined,
   HardDriveDownload,
   HardDriveUpload,
   UserRoundCheck,
   KeyRound,
   Settings,
   LogOut,
   Sparkle,
   WandSparkles,
} from 'lucide-vue-next';

const MENU_ITEMS = [
   {
      title: 'Tools',
      items: [
         {
            icon: Sparkle,
            text: 'Enhancer',
            view: 'enhancer-view',
         },
         {
            icon: WandSparkles,
            text: 'Filters',
            view: 'filters-view',
         },
      ],
   },
   {
      title: 'Accounts',
      items: [
         {
            icon: UsersRound,
            text: 'Profile',
            view: 'profile-view',
         },
         {
            icon: History,
            text: 'History',
            view: 'history-view',
         },
      ],
   },
];

const SCALE_FACTORS = [2, 4, 6, 8];

const SR_MODELS = [
   {
      text: 'Steering kernel regression',
      value: 'skr',
   },
   {
      text: 'Natural neighbor interpolation',
      value: 'nni',
   },
   {
      text: 'Bilinear interpolation',
      value: 'bilinear',
   },
   {
      text: 'Bicubic interpolation',
      value: 'bicubic',
   },
];

export { MENU_ITEMS, SCALE_FACTORS, SR_MODELS };
